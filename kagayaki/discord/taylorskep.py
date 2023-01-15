 
from kagayaki.discord import bot
from kagaconf import cfg

from hikari.events import *
from hikari.snowflakes import SnowflakeishOr, SnowflakeishSequence
from hikari.guilds import PartialGuild
import asyncio
import random
import logging
from kagayaki.discord.humanize import natural_message

TAYLOR_SWIFT_LINES = []
with open('config/dialogue/taylor_swift_lyrics.txt', 'r') as lyricsfile:
  TAYLOR_SWIFT_LINES = ["\n".join(line.split("\\n")) for line in lyricsfile.readlines() if len(line.strip()) > 0]

@bot.listen()
async def singToSkaeppy(event: MessageCreateEvent):
  skep_userid = cfg.discord.skep(0)
  if skep_userid == 0: return
  if(skep_userid in event.message.mentions.users):
    await natural_message(event.channel_id, random.choice(TAYLOR_SWIFT_LINES))