from typing import Sequence

from kagayaki.discord import bot


def contains_any(text: str, patterns: Sequence[str]):
    for p in patterns:
        if p in text:
            return True
    return False


def have_i_been_called(content: str) -> bool:
    return contains_any(content.lower(), ["kagayaki", "kagachan", "kaga-chan", "kaga chan",
                                          f"<@{bot.get_me().id}>", f"<@!{bot.get_me().id}>"])
