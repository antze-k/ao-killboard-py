#!/usr/bin/env python3

import dateutil.parser
import httpx

import argparse
import asyncio
import itertools
import os
import sys

# urls

URL_PLAYER = "https://albiononline.com/en/killboard/player/"
URL_KILL   = "https://albiononline.com/en/killboard/kill/"
URL_API    = "https://gameinfo.albiononline.com/api/gameinfo/"
URL_EVENTS = "https://gameinfo.albiononline.com/api/gameinfo/events"
URL_ITEM   = "https://gameinfo.albiononline.com/api/gameinfo/items/"

# data model

class Item:
    def __init__(self, j):
        if j is None:
            self.type = None
            self.count = None
            self.quality = None
        else:
            self.type = j["Type"]
            self.count = j["Count"]
            self.quality = j["Quality"]

    def __bool__(self):
        return self.type is not None

    def __repr__(self):
        return '<Item({})>'.format(self.type.__repr__())

class Equipment:
    def __init__(self, j):
        self.main_hand = Item(j["MainHand"])
        self.off_hand  = Item(j["OffHand"])
        self.head      = Item(j["Head"])
        self.armor     = Item(j["Armor"])
        self.shoes     = Item(j["Shoes"])
        self.bag       = Item(j["Bag"])
        self.cape      = Item(j["Cape"])
        self.mount     = Item(j["Mount"])
        self.potion    = Item(j["Potion"])
        self.food      = Item(j["Food"])

class PlayerGuild:
    def __init__(self, j):
        self.id = j["GuildId"]
        self.name = j["GuildName"]

    def __bool__(self):
        return len(self.id)>0

    def __str__(self):
        return self.name

    def __repr__(self):
        if len(self.id) == 0: return "<PlayerGuild(None)>"
        return '<PlayerGuild("{}", "{}")>'.format(
            self.id,
            self.name.replace('"','\"')
        )

class PlayerAlliance:
    def __init__(self, j):
        self.id = j["AllianceId"]
        self.name = j["AllianceName"]
        self.tag = j["AllianceTag"]

    def __bool__(self):
        return len(self.id)>0

    def __str__(self):
        return self.name

    def __repr__(self):
        if len(self.id) == 0: return "<PlayerAlliance(None)>"
        return '<PlayerAlliance("{}", "{}", "{}")>'.format(
            self.id,
            self.name.replace('"','\"'),
            self.tag.replace('"','\"')
        )

class Player:
    def __init__(self, j):
        self.id = j["Id"]
        self.name = j["Name"]
        self.guild = PlayerGuild(j)
        self.alliance = PlayerAlliance(j)
        self.equipment = Equipment(j["Equipment"])
        self.inventory = [Item(v) for v in j["Inventory"]]
        self.damage_done = j.get("DamageDone", None)
        self.average_item_power = j["AverageItemPower"]

    @property
    def url(self):
        return URL_PLAYER + self.id

    def matches(self, guild_id):
        return self.guild.id == guild_id

    def format(self):
        v = f"[{self.name}]({self.url})"
        if self.alliance or self.guild: v += ","
        if self.alliance: v += " [{}]".format(self.alliance)
        if self.guild: v += " {}".format(self.guild)
        return v

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        v = self.name
        if self.alliance or self.guild: v += ","
        if self.alliance: v += " [{}]".format(self.alliance)
        if self.guild: v += " {}".format(self.guild)
        return v

    def __repr__(self):
        return '<Player("{}", "{}", {}, {})>'.format(
            self.id,
            self.name.replace('"','\"'),
            self.guild.__repr__(),
            self.alliance.__repr__()
        )

class Event:
    def __init__(self, j):
        self.id = j["EventId"]
        self.time = dateutil.parser.parse(j["TimeStamp"])
        self.killer = Player(j["Killer"])
        self.victim = Player(j["Victim"])
        self.participants = [Player(v) for v in j["Participants"]]
        self.fame = j["TotalVictimKillFame"]

    @property
    def url(self):
        return URL_KILL + str(self.id)

    def __str__(self):
        return '{}: {} -> {}'.format(
            self.time.strftime("%Y-%m-%d %H:%M:%S"),
            self.killer,
            self.victim
        )

    def __repr__(self):
        return '<Event({}, "{}", killer={}, victim={})>'.format(
            self.id,
            self.time.strftime("%Y-%m-%d %H:%M:%S"),
            self.killer.__repr__(),
            self.victim.__repr__()
        )

def format_participant(participant, damage, type):
    s = "{} ({:.2f}%), IP=**{:d}**".format(
        participant.format(),
        (participant.damage_done or 0)*100.0/damage,
        int(participant.average_item_power)
    )
    return f"• {type}: {s}\n"

def format_event(event, guild_id):
    victory = event.killer.matches(guild_id)
    victory_str = ":muscle: Victory!" if victory else ":thumbsdown: Defeat!"

    desc1 = ""
    damage = max(1,sum(p.damage_done for p in event.participants))
    assist = []
    killer_found = False
    for p in event.participants:
        if p == event.killer:
            desc1 += format_participant(p, damage, "Killer")
            killer_found = True
        else:
            assist.append(p)
    if not killer_found:
        desc1 += format_participant(event.killer, damage, "Killer")

    assist.sort(key=lambda p: p.damage_done, reverse=True)

    for p in assist:
        desc1 += format_participant(p, damage, "Assist")

    desc1 += f"• **{event.fame}** fame gained"

    s = "{}, IP=**{:d}**".format(
        event.victim.format(),
        int(event.victim.average_item_power)
    )
    desc2 = f"• Victim: {s}\n"

    destroyed = sum(1 for item in event.victim.inventory if item)
    if destroyed:
        desc2 += f"• **{destroyed}** items destroyed\n"

    embed = {
        "color": 0x008000 if victory else 0x800000,
        "title": discord.utils.escape_markdown(
            f"{victory_str} {event.killer.name} → {event.victim.name}"
        ),
        "url": event.url,
        "fields": [
            {
                "name": "Attacking",
                "value": desc1
            },
            {
                "name": "Defending",
                "value": desc2
            }
        ],
        "footer": {
            "text": "Kill #" + str(event.id)
        },
        "timestamp": event.time.isoformat()
    }
    if event.killer.equipment.main_hand:
        embed["thumbnail"] = {
            "url": URL_ITEM+event.killer.equipment.main_hand.type
        }
    return embed

def format_bytesize(num):
    if abs(num) < 1024:
        return "{:d}B".format(num)
    num /= 1024.0
    for unit in ["Ki","Mi","Gi","Ti","Pi","Ei","Zi"]:
        if abs(num) < 1024:
            return "{:3.1f}{}B".format(num, unit)
        num /= 1024.0
    return "{:3.1f}YiB".format(num)

async def get_events(url, client, log, num=51, print_events=False, tip_time=None):
    r = f"{url}?limit={num:d}"
    if log: log.debug(f"GET {r}")
    try:
        r = await client.get(r)
        if r.status_code != 200:
            return None
    except httpx.ConnectTimeout:
        if log: log.debug("connect timeout")
        raise
    except httpx.ReadTimeout:
        if log: log.debug("read timeout")
        raise
    except httpx.TimeoutException:
        if log: log.debug("timeout")
        raise
    if log: log.debug("{} received".format(format_bytesize(len(r.content))))
    events = list(
        itertools.takewhile(
            lambda e: tip_time is None or e.time > tip_time,
            sorted((Event(e) for e in r.json()),
                   key=lambda e: e.time,
                   reverse=True)
        )
    )
    events = list(reversed(events))
    if log and print_events:
        for e in events:
            log.debug(e)
    return events

# define args

ARGS = (
    ("guild", str, "guild ID (as seen in https://albiononline.com/en/killboard/guild/[ID])", "GUILD", None),
    ("token", str, "Discord bot API token", "TOKEN", None),
    ("channel", int, "Discord channel ID", "CHANNEL", None),
    ("interval", int, "Albion Online API request interval", "SEC", 15),
    ("amount", int, "how many API events will be requested", "N", 50),
    ("debug", bool, "enable debug logging", None, False),
    ("no_default_log", bool, "disable default stdout logging", None, False)
)

# init args

def init_args(skip_argv=False):
    parser = argparse.ArgumentParser(
        prog="ao_killboard.py",
        description="Killboard bot for Albion Online",
        epilog="You can arguments (except for -h and --get) as environment values, "
               "e.g. --no-default-log as AO_KILLBOARD_NO_DEFAULT_LOG. "
               "You might want to disable default logging if you use this as a cog "
               "and prefer to set up Python logging by your own "
               "(use logging.getLogger(\"ao_killboard\"))."
    )
    parser.add_argument("--get",
                        help="only request kills once and exit",
                        action="store_true")
    for arg in ARGS:
        arg_type      = arg[1]
        env_key       = "AO_KILLBOARD_"+arg[0].upper()
        default_value = os.environ.get(env_key, arg[4])
        if default_value is not None:
            default_value = arg_type(default_value)
        if arg[4] is None:
            arg_help = "(required) "+arg[2]
        elif arg_type is bool:
            arg_help = "(optional) "+arg[2]
        else:
            arg_help = f"(optional) {arg[2]} (default: {arg[4]})"
        if arg_type is bool:
            parser.add_argument(
                "--{}".format(arg[0].replace("_","-")),
                help=arg_help,
                action="store_true",
                default=default_value
            )
        else:
            parser.add_argument(
                "--{}".format(arg[0].replace("_","-")),
                help=arg_help,
                type=arg_type,
                metavar=arg[3],
                default=default_value
            )
    if skip_argv:
        args = parser.parse_args([])
    else:
        args = parser.parse_args()
    return args

# validate

def assert_not_none(value, name):
    if value is None:
        raise ValueError(f"{name} is not set")

# launch

def _entrypoint_main():

    # aiohttp fix for Windows
    # https://github.com/aio-libs/aiohttp/issues/4324

    if os.name == 'nt':
        import aiohttp
        old = (tuple(int(v) for v in aiohttp.__version__.split(".")) < (4,))
        if old:
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy()
            )

    args = init_args()

    if args.get:
        async def get_events_once():
            try:
                import logging
                log = logging.getLogger("ao_killboard")
                log_formatter = logging.Formatter(
                    "%(message)s",
                    "%Y-%m-%d %H:%M:%S"
                )
                log_handler = logging.StreamHandler(stream=sys.stdout)
                log_handler.setFormatter(log_formatter)
                log.addHandler(log_handler)
                log.setLevel(logging.DEBUG)
                async with httpx.AsyncClient() as client:
                    await get_events(URL_EVENTS, client, log,
                                     num=10, print_events=True)
            except httpx.TimeoutException:
                pass
        asyncio.run(get_events_once())
    else:
        try:
            assert_not_none(args.token, "TOKEN")
            assert_not_none(args.guild, "GUILD")
            assert_not_none(args.channel, "CHANNEL")
        except ValueError as exc:
            parser.error(exc)

        os.environ["AO_KILLBOARD_RETAIN_ARGV"] = "1"

        import discord.ext.commands
        # no reasonable command prefix
        bot = discord.ext.commands.Bot(command_prefix="ti9uPeaGh8")
        bot.load_extension("ao_killboard")
        bot.run(args.token)
    sys.exit(0)

if __name__ == "__main__":
    _entrypoint_main()

# cog logic

import discord.ext.commands
import logging

instance = None
log = None
if os.environ.get("AO_KILLBOARD_RETAIN_ARGV", False):
    cog_args = init_args()
else:
    cog_args = init_args(skip_argv=True)

class AOKillboardCog(discord.ext.commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.task = self.bot.loop.create_task(self.wrap_process())

    def stop(self):
        if self.task is not None:
            self.task.cancel()
        self.task = None

    async def wrap_process(self):
        try:
            await self.bot.wait_until_ready()
            log.info("active")
            async with httpx.AsyncClient() as client:
                await self.process(client)
        except asyncio.CancelledError:
            raise
        except:
            exc_info = sys.exc_info()
            log.error("{}: {}".format(exc_info[0].__name__,
                                      exc_info[1]))
        finally:
            log.info("inactive")

    async def process(self, client):
        ch_not_found_timeout = 300
        retry_base = .75
        retry = retry_base
        tip_time = None
        while True:
            try:
                events = await get_events(URL_EVENTS, client, log,
                                          num=50,
                                          tip_time=tip_time)
                if events:
                    if tip_time is None:
                        # don't announce anything on first successful request
                        tip_time = events[-1].time
                        log.debug("first successful request, "
                                  "will not announce anything")
                    else:
                        tip_time = events[-1].time
                        channel = next(
                            (channel
                             for channel in self.bot.get_all_channels()
                             if channel.id == cog_args.channel),
                            None
                        )
                        if channel is None:
                            log.error(f"channel {cog_args.channel} not found")
                            log.debug(f"waiting for {ch_not_found_timeout}s")
                            await asyncio.sleep(ch_not_found_timeout)
                            continue
                        else:
                            matching_events = self.filter(events)
                            log.debug(
                                "events: new = {}, matching = {}".format(
                                    len(events),
                                    len(matching_events)
                                )
                            )
                            try:
                                await self.announce(channel, matching_events, log)
                            except discord.HTTPException:
                                exc_info = sys.exc_info()
                                log.error("{}: {}".format(exc_info[0].__name__,
                                                          exc_info[1]))
                else:
                    log.debug("events: new = 0, matching = 0")
            except httpx.TimeoutException:
                await asyncio.sleep(retry)
                log.debug(f"waiting for {retry}s")
                retry = min(retry + retry_base, cog_args.interval)
                continue
            except asyncio.CancelledError:
                raise
            except:
                exc_info = sys.exc_info()
                log.error("{}: {}".format(exc_info[0].__name__,
                                          exc_info[1]))
            retry = retry_base
            log.debug(f"waiting for {cog_args.interval}s")
            await asyncio.sleep(cog_args.interval)

    def filter(self, events):
        return [e for e in events if e.fame > 0 and self.matches(e)]

    async def announce(self, channel, events, log):
        if not events:
            return
        log.debug("events: sending to channel {}".format(channel.id))
        for e in events:
            embed = discord.Embed.from_dict(format_event(e, cog_args.guild))
            await channel.send(embed=embed)

    def matches(self, event):
        return (
            event.killer.matches(cog_args.guild) or
            event.victim.matches(cog_args.guild)
        )

def setup(bot):
    # initial logging setup

    global log
    if log is None:
        log = logging.getLogger("ao_killboard")
        if not cog_args.no_default_log:
            log_formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "%Y-%m-%d %H:%M:%S"
            )
            log_handler = logging.StreamHandler(stream=sys.stdout)
            log_handler.setFormatter(log_formatter)
            log.addHandler(log_handler)
    log.setLevel(logging.DEBUG if cog_args.debug else logging.INFO)

    # launch cog

    assert_not_none(cog_args.guild, "GUILD")
    assert_not_none(cog_args.channel, "CHANNEL")
    bot.add_cog(AOKillboardCog(bot))    
    global instance
    instance = bot.get_cog("AOKillboardCog")

def teardown(bot):
    global instance
    if instance:
        instance.stop();
        instance = None
