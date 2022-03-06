import os

import kagayaki.discord

if __name__ == "__main__":
    if os.name != "nt":
        # vastly improves performance of async python on *NIX systems, or so I'm told
        import uvloop
        uvloop.install()

    kagayaki.discord.start()
