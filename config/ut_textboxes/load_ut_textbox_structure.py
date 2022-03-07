# an awful hacky script to convert a hacked-together extracted version of the Undertale Textbox Generator's source code
# into a nice YAML structure describing the characters & expressions for each AU
import re
from collections import defaultdict
from typing import Sequence
import yaml

char_pattern = re.compile(r"^characterList \+= '"
                          r'<tr onclick="charselector\((\d+)\)">'
                          r'<td><img src="/img/generators/utgen/char_[A-Za-z0-9\-]+_([\w\-]+)\.png" alt="[^"]+"></td>'
                          r'<td>([^"]+)</td><td>([\w\-]+)</td><td>((?:[\w:\-]+|<br>|'
                          r'<span style="color:gray;">\(none\)</span>)*)</td></tr>' + "';$",
                          re.MULTILINE)

expr_pattern = re.compile(r"^expList \+= '<tr>"
                          r'<td><img src="/img/generators/utgen/char_[A-Za-z0-9\-]+_[\w\-]+\.png" alt="[^"]+"></td>'
                          r'<td>[^"]+</td><td>([\w\-]+)</td><td>((?:[\w:;).\-]+|<br>|'
                          r'<span style="color:gray;">\(none\)</span>)*)</td></tr>' + "';$", re.MULTILINE)


def charinfo_from_line(line: str) -> (str, dict):
    m = char_pattern.match(line)
    if not m:
        return None
    char_id, default_expr, display_name, internal_name, aliaslist = m.groups()
    aliases = aliaslist.split("<br>")
    if aliases[0] == '<span style="color:gray;">(none)</span>':
        aliases = []
    return internal_name, {"id": int(char_id), "name": display_name, "aliases": aliases, "default_expr": default_expr}


def charinfo_from_code(content: str) -> dict:
    aus = defaultdict(lambda: dict())
    current_au = "none"
    for line in content.split('\n'):
        char = charinfo_from_line(line)
        if char is None:
            current_au = line
        else:
            internal_name, chardict = char
            aus[current_au][internal_name] = chardict
    return aus


def exprinfo_from_line(line: str) -> (str, Sequence[str]):
    m = expr_pattern.match(line)
    if not m:
        return None
    internal_name, aliaslist = m.groups()
    aliases = aliaslist.split("<br>")
    if aliases[0] == '<span style="color:gray;">(none)</span>':
        aliases = []
    return internal_name, aliases


def exprinfo_from_code(content: str) -> dict:
    chars = defaultdict(lambda: dict())
    current_char = -1
    for line in content.split('\n'):
        expr = exprinfo_from_line(line)
        if expr is None:
            current_char = int(line)
        else:
            name, aliases = expr
            chars[current_char][name] = aliases
    return chars


if __name__ == "__main__":
    with open("ut_char_base.txt") as f:
        aus = charinfo_from_code(''.join(f.readlines()))
    with open("ut_expr_base.txt") as f:
        chars = exprinfo_from_code(''.join(f.readlines()))
    for au in aus.values():
        for char in au.values():
            char["expressions"] = chars[char["id"]]
    with open("ut_characters.yaml", "w") as f:
        yaml.dump(dict(aus), f)
