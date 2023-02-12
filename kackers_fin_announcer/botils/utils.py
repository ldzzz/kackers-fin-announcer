import json
import logging
from pathlib import Path

import discord
import namedtupled


def _get_module_logger(mod_name: str) -> logging.Logger:
    """
    To use this, do logger = get_module_logger(__name__)
    """
    logger = logging.getLogger(mod_name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] (%(name)-s:%(lineno)-s) %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger


logger = _get_module_logger(__name__)


def _load_config():
    global CFG
    with open(Path.cwd() / "config.json", "r") as fp:
        data = json.load(fp)
        CFG = namedtupled.map(data, "CFG")
    logger.info("CFG loaded")


def _cleanup_fins(fins: dict):
    """Remove duplicate fins if [v2] exist and return data as tuples"""
    logger.debug("Cleaning up finishes")
    v2s = [x.split()[0] for x in list(filter(lambda x: "v2" in x, fins.keys()))]
    ret = []
    for map, data in fins.items():
        if map in v2s:
            continue
        tmp = (map,) + tuple(data.values())
        ret.append(tmp)
    return ret


# TODO: rewrite update all users fins in db then fetch from db new fins and updated fins ??????
# TODO: why do i make my life harder
def get_updated_fins(fetched_fins: list, db_fins: dict):
    """For given player get new fins/PBs."""
    new_fins = []
    pb_fins = []
    for m in fetched_fins[:2]:
        # db_fins.pop(map[0], None)
        print(m)
        dbmap = db_fins.get(m[0], None)
        if dbmap is not None:  # pb
            if m[3] > dbmap["date"] and m[1] < dbmap["score"]:
                delta = dbmap["score"] - m[1] + 1
                pb_fins.append((delta,) + m[::-1])
        else:  # new fin
            new_fins.append(m)

    return new_fins, pb_fins


# TODO: this can use rewrite
def build_announce_embed(player: tuple, fin: tuple) -> discord.Embed:
    logger.debug("Building announce embed")
    mytitle = ":checkered_flag: NEW FINISH :checkered_flag:"
    delta = ""
    if len(fin) > 4:
        delta = f" (-{fin[4] / 1000.0})"
        mytitle = ":fire: NEW PB :fire:"
    fin_embed = discord.Embed(
        title=mytitle,
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        color=discord.Color.random(),
    )
    fin_embed.set_thumbnail(url=CFG.thumbnails.replace("MAPNR", fin[0].split()[0]))
    fin_embed.add_field(name="Player", value=player[0])
    fin_embed.add_field(name="\u200B", value="\u200B")  # newline
    fin_embed.add_field(name="Map", value=f"#{fin[0]}")
    fin_embed.add_field(name="Time", value=f"{fin[1] / 1000.0}s{delta}")
    fin_embed.add_field(name="\u200B", value="\u200B")  # newline
    fin_embed.add_field(name="Rank", value=fin[2])
    fin_embed.add_field(name="Total fins", value=f"{player[1]}/225")
    fin_embed.add_field(name="\u200B", value="\u200B")  # newline
    fin_embed.add_field(name="Date", value=f"<t:{int(fin[3])}:f>")
    fin_embed.set_footer(text=f"Bot by djinn")
    return fin_embed
