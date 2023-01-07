from kagayaki.discord import bot
from kagaconf import cfg

from hikari.events import *
from hikari.snowflakes import SnowflakeishOr, SnowflakeishSequence
from hikari.guilds import PartialGuild
import asyncio
import random
import logging

log = logging.getLogger(__name__)

def random_color():
    return "#"+"".join(random.choices("0123456789ABCDEF", k=6))

async def reroll_color(guild: int):
    role = cfg.discord.guilds[guild].random.role_id(0)
    if role == 0: 
        return
    await bot.rest.edit_role(guild, role, color=random_color())

@bot.listen()
async def test_reroll(event: MessageCreateEvent):
    if event.content == "reroll":
        await reroll_color(event.message.guild_id)

async def reroll_loop(guild: int):
    while True:
        await reroll_color(guild)
        wait_time = max(random.gauss(cfg.discord.guilds[guild].random.average(60), cfg.discord.guilds[guild].random.stddev(20)),0)
        log.info(f"did a reroll in guild {guild}, scheduled in {wait_time} seconds")
        await asyncio.sleep(wait_time)


@bot.listen()
async def init_hooks(event: GuildAvailableEvent):
    await reroll_loop(int(event.guild_id))