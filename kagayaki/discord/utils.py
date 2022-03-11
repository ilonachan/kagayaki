import logging
from typing import Sequence

from hikari.guilds import Member

from kagayaki.discord import bot
from kagaconf import cfg

log = logging.getLogger(__name__)

def contains_any(text: str, patterns: Sequence[str]):
    if text is None:
        return False
    for p in patterns:
        if p in text:
            return True
    return False


def have_i_been_called(content: str) -> bool:
    if content is None:
        return False
    return contains_any(content.lower(), ["kagayaki", "kagachan", "kaga-chan", "kaga chan",
                                          f"<@{bot.get_me().id}>", f"<@!{bot.get_me().id}>"])


def is_allowed_to_send(user: Member):
    mute_roles = cfg.discord.guilds[user.guild_id].mute_roles([])
    if len([v for v in mute_roles if v in user.role_ids]) > 0:
        return False
    return True
