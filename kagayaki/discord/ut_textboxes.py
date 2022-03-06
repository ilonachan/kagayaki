from enum import Enum
from typing import Optional
from urllib.parse import quote
from typing import TypeVar, Generic

import lightbulb
import requests
import os.path

from kagayaki.discord import bot, send_as_webhook


class TextBoxBorder(Enum):
    UNDERTALE = "undertale"
    DELTARUNE = "deltarune"
    EARTHBOUND = "earthbound"
    UNDERSWAP = "underswap"
    UNDERFELL = "underfell"
    OCTAGONAL = "octagonal"
    SHADEDGROUND = "shadedground"
    TUBERTALE = "tubertale"
    STUBERTALE = "stubertale"
    FNASTALE = "fnastale"
    DERP = "derp"


class TextBoxFont(Enum):
    DETERMINATION = "determination"
    SANS = "sans"
    PAPYRUS = "papyrus"
    EARTHBOUND = "earthbound"
    WINGDINGS = "wingdings"


def url_from_params(text: str, *, img_format: str = "png", animate: bool = False,
                    box: TextBoxBorder = TextBoxBorder.UNDERTALE,
                    font: TextBoxFont = TextBoxFont.DETERMINATION,
                    boxcolor: str = "ffffff", charcolor: Optional[str] = None, asteriskcolor: Optional[str] = None,
                    character: Optional[str] = None, expression: Optional[str] = None, image_url: Optional[str] = None,
                    small=False, border=False, darkworld=False):
    # format is "png" or "gif"

    # boxcolor, charcolor and asteriskcolor can be any hex color, some predefined values exist but I won't bother yet

    # character: lots of characters across AUs, or "blank"
    # expression: specific to each character

    if animate:
        img_format = "gif"

    url = f"https://www.demirramon.com/gen/undertale_text_box.{img_format}?text={quote(text)}" \
          f"&box={box.value}&font={font.value}&boxcolor={boxcolor}"
    if image_url is not None:
        url += f"&character=custom&url={quote(image_url)}"
    elif character is not None:
        url += f"&character={character}"
        if expression is not None:
            url += f"&expression={expression}"

    if charcolor is not None:
        url += f"&charcolor={charcolor}"
    if asteriskcolor is not None:
        url += f"&asteriskcolor={asteriskcolor}"
    if small:
        url += "&small=true"
    if border:
        url += "&border=true"
    url += "&mode=" + ("darkworld" if darkworld else "regular")
    if img_format == "gif":
        url += f"&animate={str(animate).lower()}"

    return url


def fetch_text_box(url, filename=None, img_format="png"):
    r = requests.get(url, stream=True)
    if filename is None:
        counter = 0
        filename = 'undertale_text_box.' + img_format
        while os.path.exists(filename):
            counter += 1
            filename = f'undertale_text_box_{counter}.{img_format}'

    with open(filename, 'wb') as f:
        f.write(r.content)
    return filename


@bot.command
@lightbulb.option("text", "content of the text box", str, required=True)
@lightbulb.option("character", "character to be used", str, required=False)
@lightbulb.option("expression", "expression of the character", str, required=False)
@lightbulb.option("image_url", "url pointing to a character sprite", str, required=False)
@lightbulb.option("box", "text box design", str,
                  default=TextBoxBorder.UNDERTALE.value, choices=[el.value for el in TextBoxBorder])
@lightbulb.option("font", "text box font", str,
                  default=TextBoxFont.DETERMINATION.value, choices=[el.value for el in TextBoxFont])
@lightbulb.option("boxcolor", "color of the text box", str, default="ffffff")
@lightbulb.option("charcolor", "color of the text", str, required=False)
@lightbulb.option("asteriskcolor", "color of the asterisk, if it's there", str, required=False)
@lightbulb.option("animate", "animate the text appearing", bool, default=False)
@lightbulb.option("small", "small text box", bool, default=False)
@lightbulb.option("border", "should there be a wider border around the text box", bool, default=False)
@lightbulb.option("darkworld", "text box mode (no idea what this means)", bool, default=False)
@lightbulb.option("anonymous", "should the text box be sent under kaga-chan's name", bool, default=False)
@lightbulb.command("utbox", description="create an undertale textbox", ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def utbox_command(ctx: lightbulb.Context):
    options = ctx.raw_options
    options["box"] = TextBoxBorder(options["box"])
    options["font"] = TextBoxFont(options["font"])
    anonymous = options["anonymous"]
    del options["anonymous"]
    url = url_from_params(**options)
    await ctx.respond("\N{ZERO WIDTH NON-JOINER}❤", delete_after=None)
    if anonymous:
        await bot.rest.create_message(ctx.channel_id, url)
    else:
        await send_as_webhook(ctx.channel_id, url, user=ctx.user)


if __name__ == '__main__':
    myurl = url_from_params('looking good, kiddo', character='sans', expression="blue-eye")
    print(myurl)
    image = fetch_text_box(myurl)
