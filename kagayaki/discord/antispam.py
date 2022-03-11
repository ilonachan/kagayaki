import asyncio
from datetime import datetime, timedelta
from collections import defaultdict, deque
from math import ceil
import random

import pytz
from hikari import ForbiddenError
from hikari.users import PartialUser
from hikari.events import GuildMessageCreateEvent
from hikari.snowflakes import SnowflakeishOr, Snowflake
from hikari.messages import PartialMessage
from kagaconf import cfg

from kagayaki.discord import bot
from kagayaki.discord.humanize import run_sequence

LINE_LENGTH = 120


def message_length(message: PartialMessage | str):
    if isinstance(message, str):
        content: str = message
    else:
        content: str = message.content
    if content is None:
        return 0

    line_count = sum(ceil(max(len(line), 1) / LINE_LENGTH) for line in content.split('\n'))
    return line_count


short_history = defaultdict(lambda: deque())
user_spam_status = defaultdict(lambda: 0)
user_spam_lock = defaultdict(lambda: asyncio.Lock())
cooldown = datetime.now(tz=pytz.UTC)


async def is_spam(message: PartialMessage) -> bool:
    # there are channels where unlimited spamming is permitted
    if message.channel_id in cfg.discord.guilds[message.guild_id].spam_allowed([]):
        return False
    # the written message is ABSOLUTELY MASSIVE (actually maybe this is not a good idea, let's see)
    if message_length(message) > 20:
        return True
    # the user has been writing a lot of long messages in a very short amount of time
    if recent_length(message.author, lookback=timedelta(seconds=5)) > 10 and \
            recent_messages(message.author, lookback=timedelta(seconds=5)) > 4:
        return True
    return False


def recent_length(author: SnowflakeishOr[PartialUser], lookback: timedelta = timedelta(seconds=30)):
    if isinstance(author, PartialUser):
        author: Snowflake = author.id
    threshold = datetime.now(tz=pytz.UTC) - lookback
    return sum(msg[1] for msg in short_history[author] if msg[0] < threshold)


def recent_messages(author: SnowflakeishOr[PartialUser], lookback: timedelta = timedelta(seconds=30)):
    if isinstance(author, PartialUser):
        author: Snowflake = author.id
    threshold = datetime.now(tz=pytz.UTC) - lookback
    return sum(1 for msg in short_history[author] if msg[0] < threshold)


def update_metrics(event):
    short_history[event.author_id].append((event.message.created_at, message_length(event.message)))
    for msg in list(short_history[event.author_id]):
        # only keep messages from up to 30s ago
        if msg[0] < datetime.now(tz=pytz.UTC) - timedelta(seconds=30):
            short_history[event.author_id].remove(msg)


@bot.listen()
async def detect_spam_messages(event: GuildMessageCreateEvent):
    if event.author.is_bot:
        return
    global cooldown

    lock: asyncio.Lock = user_spam_lock[event.author_id]
    if lock.locked():
        return
    async with lock:
        update_metrics(event)
        if await is_spam(event.message):
            if cooldown < datetime.now(tz=pytz.UTC) - timedelta(seconds=3):
                user_spam_status[event.author_id] += 1
                choices = cfg.humanize.dialogue.antispam.main([])
                if user_spam_status[event.author_id] == 4:
                    choices = cfg.humanize.dialogue.antispam.last_warning([])
                if user_spam_status[event.author_id] > 4:
                    choices = cfg.humanize.dialogue.antispam.punish([])
                    try:
                        await event.member.edit(communication_disabled_until=datetime.now(tz=pytz.UTC)+timedelta(minutes=5),
                                                reason="was spamming a lot. If I've made a mistake please tell mommy @ilonachan")
                    except ForbiddenError:
                        choices = cfg.humanize.dialogue.antispam.punish_err([])
                    user_spam_status[event.author_id] = 1
                choice = random.choice(choices)
                await run_sequence(event.channel_id, choice, user=event.member, guild_id=event.guild_id)
                cooldown = datetime.now(tz=pytz.UTC)
        else:
            if recent_length(event.author) < 10:
                user_spam_status[event.author_id] = max(user_spam_status[event.author_id]-1, 0)

