import logging

from hikari.events import *

import numpy as np
import re
import random
import asyncpraw

from asyncio import sleep
from kagaconf import cfg

from kagayaki.discord import bot
from kagayaki.discord.humanize import natural_message
from kagayaki.discord.utils import have_i_been_called

log = logging.getLogger(__name__)


class JokeAborted(Exception):
    pass


async def knockknockjoke(event: MessageCreateEvent):
    choices = cfg.humanize.dialogue.knockknock.main([])
    if len(choices) == 0:
        raise ValueError
    setup, payoff = np.random.choice(choices).split(' | ')
    count = 3
    while count > 0:
        await natural_message(event.channel_id, "knock knock")
        e = await bot.wait_for(MessageCreateEvent, None, lambda e: event.author_id == e.author_id)
        if not re.match(r".*\W*who'?s\s+there\??\W*", e.content, re.IGNORECASE | re.DOTALL | re.UNICODE):
            count -= 1
            if count == 0:
                break
            choices = cfg.humanize.dialogue.knockknock.fail([]) + cfg.humanize.dialogue.knockknock.fail_who([])
            if len(choices) > 0:
                await natural_message(event.channel_id, np.random.choice(choices))
            continue
        await natural_message(event.channel_id, setup)
        e = await bot.wait_for(MessageCreateEvent, None, lambda e: event.author_id == e.author_id)
        if not re.match(r".*\W*" + setup + r"\s+who\??\W*", e.content, re.IGNORECASE | re.DOTALL | re.UNICODE):
            count -= 1
            if count == 0:
                break
            choices = cfg.humanize.dialogue.knockknock.fail([]) + cfg.humanize.dialogue.knockknock.fail_rep([])
            if len(choices) > 0:
                await natural_message(event.channel_id, np.random.choice(choices))
            continue
        await natural_message(event.channel_id, payoff)
        break
    if count == 0:
        raise JokeAborted()


async def rslashjokes(event: MessageCreateEvent, subreddit="ProgrammerDadJokes"):
    try:
        async with asyncpraw.Reddit(
                client_id=cfg.reddit.client_id(),
                client_secret=cfg.reddit.client_secret(),
                user_agent=cfg.reddit.user_agent(),
        ) as reddit:
            values = []
            sub = await reddit.subreddit(subreddit)
            async for submission in sub.hot(limit=20):
                values.append((submission.title, submission.selftext, submission.over_18))
            if len(values) == 0:
                raise ValueError
            title, text, over_18 = random.choice(values)
            if over_18:
                await natural_message(event.channel_id, "oooh, this one's naughty ( ͡° ͜ʖ ͡°)")
                await sleep(.5)
            await natural_message(event.channel_id, "**" + title + "**\n" + text)
    except Exception as e:
        log.error("something went wrong while fetching Reddit", exc_info=e)
        raise ValueError


async def normaljokes(event: MessageCreateEvent):
    choices = cfg.humanize.dialogue.jokes.main([])
    if len(choices) > 0:
        await natural_message(event.channel_id, np.random.choice(choices))
    else:
        raise ValueError


@bot.listen()
async def crackajoke(event: MessageCreateEvent):
    if have_i_been_called(event.content) and\
            re.match(r"(.*\W)?tell\s+(me\s+)?a(nother)?\s+(knock\s*knock\s+|normal\s+)?joke(\W.*)?",
                     event.content, re.IGNORECASE | re.DOTALL):
        if np.random.random() > 0.6:
            choices = cfg.humanize.dialogue.jokes.before([])
            if len(choices) > 0:
                await natural_message(event.channel_id, np.random.choice(choices))
        try:
            joke_sources = {
                "default": normaljokes,
                "knockknock": knockknockjoke,
                "reddit": rslashjokes
            }
            if "from reddit" in event.content.lower():
                await rslashjokes(event)
            if m := re.match(r".*from\s+r/([a-zA-Z_\-+0-9]{3,21}).*", event.content.lower(), re.IGNORECASE | re.DOTALL):
                await rslashjokes(event, subreddit=m.group(1))
            elif "normal" in event.content.lower():
                await normaljokes(event)
            elif re.match(r".*\s+knock\s*knock\s+.*", event.content, re.IGNORECASE | re.DOTALL):
                await knockknockjoke(event)
            else:
                keys = ["default", "knockknock", "reddit"]
                p = [0.0000000001, 0.6, 0.4]
                for key in np.random.choice(keys, size=len(keys), replace=False, p=p):
                    try:
                        await joke_sources[key](event)
                        break
                    except ValueError as e:
                        log.error(f"failed to load {key} joke", exc_info=e)

            if np.random.random() > 0.4:
                choices = cfg.humanize.dialogue.jokes.after([])
                if len(choices) > 0:
                    await sleep(.6)
                    await natural_message(event.channel_id, np.random.choice(choices))
        except JokeAborted:
            choices = cfg.humanize.dialogue.jokes.abort([])
            if len(choices) > 0:
                await natural_message(event.channel_id, np.random.choice(choices))
        except ValueError:
            await natural_message(event.channel_id, "sry, I can't find any jokes rn :(")
