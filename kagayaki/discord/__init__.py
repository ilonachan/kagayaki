import logging

from typing import Any, Sequence, Union, Optional

import hikari
import lightbulb
from hikari import Embed, Resourceish, UNDEFINED, UndefinedOr, PartialRole, URL, \
    UndefinedType, Message
from hikari.errors import NotFoundError, ForbiddenError
from hikari.api import ComponentBuilder
from hikari.snowflakes import Snowflakeish, SnowflakeishOr, SnowflakeishSequence
from hikari.events import *
from hikari.presences import Status, Activity, ActivityType
from hikari.channels import *
from hikari.users import *
from hikari.webhooks import IncomingWebhook, ExecutableWebhook
from kagaconf import cfg

log = logging.getLogger(__name__)

# permissions: 544320384112
bot = lightbulb.BotApp(intents=hikari.Intents.ALL, banner=None,
                       token=cfg.discord.bot_token(), default_enabled_guilds=cfg.discord.slash_command_guilds([]))

webhooks: dict[Snowflakeish, ExecutableWebhook] = {}


async def send_as_webhook(
        channel: SnowflakeishOr[TextableChannel],
        content: UndefinedOr[Any] = UNDEFINED, *,
        user: UndefinedOr[SnowflakeishOr[User]] = UNDEFINED,
        username: UndefinedOr[str] = UNDEFINED, avatar_url: Union[UndefinedType, str, URL] = UNDEFINED,
        attachment: UndefinedOr[Resourceish] = UNDEFINED, attachments: UndefinedOr[Sequence[Resourceish]] = UNDEFINED,
        component: UndefinedOr[ComponentBuilder] = UNDEFINED,
        components: UndefinedOr[Sequence[ComponentBuilder]] = UNDEFINED,
        embed: UndefinedOr[Embed] = UNDEFINED, embeds: UndefinedOr[Sequence[Embed]] = UNDEFINED,
        tts: UndefinedOr[bool] = UNDEFINED, mentions_everyone: UndefinedOr[bool] = UNDEFINED,
        user_mentions: UndefinedOr[Union[SnowflakeishSequence[PartialUser], bool]] = UNDEFINED,
        role_mentions: UndefinedOr[Union[SnowflakeishSequence[PartialRole], bool]] = UNDEFINED) -> Optional[Message]:

    if user is not UNDEFINED:
        if username is UNDEFINED or avatar_url is UNDEFINED:
            if not isinstance(user, User):
                user = await bot.rest.fetch_user(user)
            if username is UNDEFINED:
                username = user.username
            if avatar_url is UNDEFINED:
                avatar_url = user.make_avatar_url()

    try:
        if int(channel) not in webhooks:
            try:
                whs = await bot.rest.fetch_channel_webhooks(channel)
            except NotFoundError:
                log.info("Hikari has not yet implemented threads, and possibly webhooks can't be used in threads")
                return None
            for wh in whs:
                if isinstance(wh, IncomingWebhook) and wh.name == f'kgyk-{int(channel)}':
                    log.info(f'Webhook for channel {int(channel)} was found, reusing')
                    webhooks[int(channel)] = wh
                    break
            else:
                log.info(f'No existing webhook for channel {int(channel)} was found, creating')
                webhooks[int(channel)] = await bot.rest.create_webhook(channel, f'kgyk-{int(channel)}')
        webhook: ExecutableWebhook = webhooks[int(channel)]

        try:
            return await webhook.execute(content=content, username=username, avatar_url=avatar_url,
                                         attachment=attachment, attachments=attachments,
                                         component=component, components=components,
                                         embed=embed, embeds=embeds, tts=tts,
                                         mentions_everyone=mentions_everyone,
                                         user_mentions=user_mentions, role_mentions=role_mentions)
        except NotFoundError:
            log.info(f'Previously known webhook for channel {int(channel)} was deleted, recreating')
            webhooks[int(channel)] = await bot.rest.create_webhook(channel, f'kgyk-{int(channel)}')
            return await webhook.execute(content=content, username=username, avatar_url=avatar_url,
                                         attachment=attachment, attachments=attachments,
                                         component=component, components=components,
                                         embed=embed, embeds=embeds, tts=tts,
                                         mentions_everyone=mentions_everyone,
                                         user_mentions=user_mentions, role_mentions=role_mentions)
    except ForbiddenError:
        log.warning(f'Insufficient permissions for creating fancy webhooks')
        return None


def start():
    bot.run(status=Status.ONLINE, activity=Activity(type=ActivityType.PLAYING, name="human"))


# I know I'm breaking PEP8, but I legit have no idea where else I should be putting this
import kagayaki.discord.autoreact
import kagayaki.discord.humanize
import kagayaki.discord.jokes
import kagayaki.discord.ut_textboxes
# nothing but trouble, this one
#import kagayaki.discord.antispam
import kagayaki.discord.randomrole
import kagayaki.discord.taylorskep