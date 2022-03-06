import asyncio
import logging

import numpy as np

from kagayaki.discord import bot
from hikari.events import *

from kagaconf import cfg

from kagayaki.discord.utils import contains_any, have_i_been_called

log = logging.getLogger(__name__)


@bot.listen()
async def at_someone(event: GuildMessageCreateEvent):
    someone_role = cfg.discord.guilds[event.guild_id].someone_role(0)
    if someone_role != 0 and someone_role in event.message.mentions.role_ids:
        members = [m async for m in bot.rest.fetch_members(event.guild_id) if not m.is_bot and m.id != event.author_id]
        if len(members) == 0:
            await event.message.respond("aww you're lonely :( but I'm always here for you ❤")
            return
        target = np.random.choice(members)
        await event.message.respond(f'{target.mention}')


@bot.listen()
async def someone_emptyrole(event: MemberUpdateEvent):
    someone_role = cfg.discord.guilds[event.guild_id].someone_role(0)
    if someone_role != 0 and someone_role in event.member.role_ids:
        await event.member.remove_role(someone_role)
        log.warning(f"someone tried to give the @someone role to {event.member.display_name}, not cool >:(")


@bot.listen()
async def autoreact(event: GuildMessageCreateEvent):
    waiting_time = np.random.beta(2.5, 8)*0.6
    await asyncio.sleep(waiting_time)
    content = event.message.content
    if contains_any(content, ["DETERMINATION", "DETERMINED"]) and \
            (dt_emote := cfg.discord.guilds[event.guild_id].dt_emote(0)) != 0:
        await event.message.add_reaction('determination', dt_emote)
    if "MURDER" in content:
        await event.message.add_reaction("\N{HOCHO}")
    if "KINDNESS" in content:
        await event.message.add_reaction("\N{GREEN HEART}")
    if have_i_been_called(content):
        if event.author_id == bot.get_me().id:
            return
        await event.message.add_reaction("\N{SPARKLES}")


@bot.listen()
async def stabby_message(event: GuildMessageCreateEvent):
    if event.author.is_bot:
        return

    stabby_role = cfg.discord.guilds[event.guild_id].stabby_role(0)
    if stabby_role == 0:
        return
    if stabby_role in (await bot.rest.fetch_member(event.guild_id, event.author_id)).role_ids:
        await event.message.add_reaction("\N{HOCHO}")
        prev_msg = await bot.rest.fetch_messages(event.channel_id, before=event.message).limit(1).next()
        await prev_msg.remove_reaction("\N{HOCHO}")


@bot.listen()
async def stabby_reaction(event: GuildReactionAddEvent):
    if event.member.is_bot:
        return

    stabby_role = cfg.discord.guilds[event.guild_id].stabby_role(0)
    if stabby_role == 0:
        return
    if event.emoji_name == "\N{HOCHO}":
        await bot.rest.add_role_to_member(event.guild_id, event.user_id, stabby_role)
    if event.emoji_name == "\N{GREEN HEART}":
        await bot.rest.remove_role_from_member(event.guild_id, event.user_id, stabby_role)
