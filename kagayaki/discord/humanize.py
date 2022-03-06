import asyncio
import logging
import random
import re

from asyncio import sleep
from typing import Any, Sequence, Union

import numpy as np
from kagaconf import cfg

from kagayaki.discord import bot
from hikari.events import *
from hikari.snowflakes import SnowflakeishOr, SnowflakeishSequence
from hikari.channels import TextableChannel
from hikari.undefined import *
from hikari.guilds import PartialRole
from hikari.users import PartialUser
from hikari.messages import PartialMessage, Message
from hikari.files import Resourceish

log = logging.getLogger(__name__)


from kagaconf import cfg


def resolve_config(content: str, **kwargs) -> str:
    def process_config(m: re.Match):
        res = eval(m.group(1), {'cfg': cfg, **kwargs})
        return str(res)
    return re.sub(r"{(cfg\.[^}]+)}", process_config, content)


async def natural_message(channel: SnowflakeishOr[TextableChannel],
                          content: UndefinedOr[Any] = UNDEFINED,
                          *,
                          attachment: UndefinedOr[Resourceish] = UNDEFINED,
                          attachments: UndefinedOr[Sequence[Resourceish]] = UNDEFINED,
                          # component: UndefinedOr[ComponentBuilder] = UNDEFINED,
                          # components: UndefinedOr[Sequence[ComponentBuilder]] = UNDEFINED,
                          # embed: UndefinedOr[Embed] = UNDEFINED,
                          # embeds: UndefinedOr[Sequence[Embed]] = UNDEFINED,
                          tts: UndefinedOr[bool] = UNDEFINED,
                          # nonce: UndefinedOr[str] = UNDEFINED,
                          reply: UndefinedOr[SnowflakeishOr[PartialMessage]] = UNDEFINED,
                          mentions_everyone: UndefinedOr[bool] = UNDEFINED,
                          mentions_reply: UndefinedOr[bool] = UNDEFINED,
                          user_mentions: UndefinedOr[Union[SnowflakeishSequence[PartialUser], bool]] = UNDEFINED,
                          role_mentions: UndefinedOr[Union[SnowflakeishSequence[PartialRole], bool]] = UNDEFINED,
                          cps: float = 80,  # this is surprisingly low, maybe ppl on discord just type slow?
                          **kwargs) -> Message:
    """
    calculate a realistic typing time for the provided message, optimally factoring in special characters,
    attachments etc. Then start typing, and after the appropriate amount of time send the message.

    Certain features like embeds or UI components, which can only be efficiently used by bots,
    are not included in this function signature (although this is easily changeable later). Similarly, the `nonce`
    feature that I have never used is something only a bot can use, so it is not included.

    All present parameters except `cps` are simply passed through to `bot.rest.create_message()`, and I will
    only describe their contribution to the typing time.

    :param channel:
    :param content: the main factor determining typing time, its length divided by `cps` and multiplied by
                    random fuzziness gives the baseline.
                    TODO: count special characters & add additional time for each one
    :param attachment: counts as a 1-element list for `attachments`.
    :param attachments: each attachment adds ~5s to the waiting time
    :param tts:
    :param reply:
    :param mentions_everyone:
    :param mentions_reply:
    :param user_mentions:
    :param role_mentions:
    :param cps: the typing speed of the bot in characters/second
    :return:
    """
    content = resolve_config(str(content), **kwargs)
    content = content.format(**kwargs)

    # typing speed is the baseline for how long messages take to compose
    waiting_time = len(content) / cps * np.random.normal(1, 0.05)

    # humans need a bit of time to attach things to messages
    if attachments is not UNDEFINED:
        attachments: Sequence[Resourceish]
        attachment_count = len(attachments)
    elif attachment is not UNDEFINED:
        attachment_count = 1
    else:
        attachment_count = 0
    waiting_time += 5 * attachment_count * np.random.normal(1, 0.1)

    await bot.rest.trigger_typing(channel)
    await asyncio.sleep(waiting_time)
    return await bot.rest.create_message(channel, content,
                                         attachment=attachment, attachments=attachments, tts=tts, reply=reply,
                                         mentions_everyone=mentions_everyone, mentions_reply=mentions_reply,
                                         user_mentions=user_mentions, role_mentions=role_mentions)


async def run_sequence(channel: SnowflakeishOr[TextableChannel], sequence: Sequence[dict], **kwargs):
    for item in sequence:
        if "msg" in item:
            await natural_message(channel, item["msg"], user_mentions=True, **kwargs)
        if "wait" in item:
            await sleep(item["wait"])


@bot.listen()
async def say_hi(event: GuildAvailableEvent):
    general_channel_id = cfg.discord.guilds[event.guild_id].general_channel(0)
    if general_channel_id == 0:
        # is it possible to somehow figure out which channel is the main one?
        # we'll just give up for now
        return
    # await bot.rest.edit_my_member(event.guild_id, nickname="kagachan")
    choice = random.choice(cfg.humanize.dialogue.restart())
    await run_sequence(general_channel_id, choice, guild_id=event.guild_id)


@bot.listen()
async def join(event: GuildJoinEvent):
    general_channel_id = cfg.discord.guilds[event.guild_id].general_channel(0)
    if general_channel_id == 0:
        # is it possible to somehow figure out which channel is the main one?
        # we'll just give up for now
        return
    await run_sequence(general_channel_id, cfg.humanize.dialogue.server_join()[0])
