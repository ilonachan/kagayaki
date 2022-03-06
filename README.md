# KAGAYAKI

The spiritual successor to [gmsh](https://github.com/ilonachan/gmsh),
a private bot for a little server I'm helping moderate.

Right now the following features are implemented:
- auto-reactions (some UNDERTALE themed, some inside jokes that stuck around, possibly more to come)
- I have mastered the art of webhook bot messages (cool) so I'll try to use those a lot
- UNDERTALE-style text boxes with slash commands (new)
- kaga-chan can tell bad jokes (new)
- a little anti-spam feature, which needs to be tested for practicality or annoying-ness (new)

Some of the features of gmsh that might be carried over at a later point include:
- a shell-like syntax for some techy commands
- A puppeteering feature to allow anyone to roleplay with the bot (all messages should be properly sanitized)

If there are any instances of hardcoded user/channel/server ids, that should be changed
to a database-managed system. Not least because I like to publish my work, and I don't
like doxxing people. For now I'll just hardcode these things in a config file or sth.
Also a web interface would be cool, but yea that's not happening anytime soon.

# Installation

All the required libraries are listed in the `requirements.txt` file. I don't know the exact
requirements of hikari and other libraries, but I recommend using Python 3.10 because that's
what I'm developing with. Some older versions might work too.

To simply run the bot in a docker container, execute `run_container.sh`.
This will build the container from source, and deploy it mounting the provided default paths.

Some information I cannot provide in this repository for security reasons:
this naturally includes the bot token, as well as some private information regarding our server.
Example files starting with _ are provided to detail the required file structure,
fill in your own details to execute. None of this should require changing the container itself.

# License

I wrote all the code in this repository purely for private use. But in the unlikely event that
any of it is helpful/inspirational to you, feel free to use it. I provide no guarantees for anything,
what you do with your systems is your own responsibility, not liable yada yada. Go nuts.

_(Just don't tell anyone about K's real name.)_
