# ao_killboard.py

A minimalistic Discord bot for Albion Online's killboard.

## Getting Started

### Prerequisites
* [Python >= 3.6](https://www.python.org/downloads/)

### Built with:
* [discord.py](https://discordpy.readthedocs.io/en/latest/index.html)
* [httpx](https://www.python-httpx.org/)

### Getting the bot
```
git clone https://github.com/antze-k/ao-killboard-py
python3 -mpip install -r ao-killboard-py/requirements.txt
```
Change your working directory to `cd ao-killboard-py/src` and run the bot with either of those, depending on your system setup:
* `python3 ao_killboard.py`
* `python ao_killboard.py`
* `ao_killboard.py`
* `./ao_killboard.py`

The documentation will refer to `ao_killboard.py` further for simplicity.

### Creating a bot account and setting it up for your server (guild)
* [https://discordpy.readthedocs.io/en/latest/discord.html](https://discordpy.readthedocs.io/en/latest/discord.html)
* [https://discordpy.readthedocs.io/en/latest/discord.html#inviting-your-bot](https://discordpy.readthedocs.io/en/latest/discord.html#inviting-your-bot) (you don't have to add any specific permissions here, if you choose to add Send Messages permission manually for your channel)
* [Setting permissions](https://support.discordapp.com/hc/en-us/articles/206029707-How-do-I-set-up-Permissions-) (scroll down to Channel Permissions)

### Configure and run
Set up three parameters (guild, token and channel) either using environment variables or using command line arguments.
* "guild" is your Albion Online guild identifier (as seen in https://albiononline.com/en/killboard/guild/**ID**)
* "token" is your bot token obtained in the previous step
* "channel" is the Discord channel ID the bot will post messages into (check [this article](https://support.discordapp.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-) if you need to know how to obtain it)

You can always run `ao_killboard.py --help` to check the available options.

#### Running the bot manually using command line arguments
```ao_killboard.py --guild <GUILD-ID> --token <DISCORD-TOKEN> --channel <123456789>```
Replace the <PLACEHOLDERS> with their respective values, omitting angle brackets.

#### Running the bot using environment values and a batch script (Windows)
Paste the following into a file with a name like "start-bot.cmd":
```
@echo off
set AO_KILLBOARD_GUILD=<GUILD-ID>
set AO_KILLBOARD_TOKEN=<DISCORD-TOKEN>
set AO_KILLBOARD_GUILD=<123456789>
ao_killboard.py %*
```
Replace the <PLACEHOLDERS> with their respective values, omitting angle brackets.

#### Running the bot using environment values and a shell script (POSIX-like OS)
Paste the following into a file with a name like "start-bot.sh":
```
AO_KILLBOARD_GUILD=<GUILD-ID>
AO_KILLBOARD_TOKEN=<DISCORD-TOKEN>
AO_KILLBOARD_GUILD=<123456789>
exec ao_killboard.py "$@"
```
Replace the <PLACEHOLDERS> with their respective values, omitting angle brackets. Set the execute bit by running `chmod +x start-bot.sh`.
