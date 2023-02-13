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
    logger.setLevel(logging.INFO)
    return logger


logger = _get_module_logger(__name__)


def _load_config():
    global CFG
    with open(Path.cwd() / "config.json", "r") as fp:
        data = json.load(fp)
        CFG = namedtupled.map(data, "CFG")
    logger.info("CFG loaded")


def _cleanup_fins(fins: dict):
    """Remove fins that have v2 versions (KR specific)"""
    ret = []
    for map, data in fins.items():
        if map in CFG.maps_exclude_list:
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
    for m in fetched_fins:
        dbmap = db_fins.get(m[0], None)
        if dbmap is not None:  # pb
            if m[3] > dbmap["date"] and m[1] < dbmap["score"]:
                delta = dbmap["score"] - m[1] + 1
                pb_fins.append((delta,) + m[::-1])
        else:  # new fin
            new_fins.append(m)

    return new_fins, pb_fins


def _score_to_string(score: int, delta: int = None) -> str:
    """Converts map score to a string with seconds representation."""
    diff = ""
    if delta is not None:
        diff = f" (-{delta / 1000.0})"
    return f"{score / 1000.0}s{diff}"


# TODO: this can use rewrite
def build_announce_embed(player: tuple, fin: tuple) -> discord.Embed:
    logger.debug("Building announce embed")
    mytitle = ":checkered_flag: NEW FINISH :checkered_flag:"
    delta = None
    if len(fin) > 4:
        delta = fin[4]
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
    fin_embed.add_field(name="Time", value=_score_to_string(fin[1], delta))
    fin_embed.add_field(name="\u200B", value="\u200B")  # newline
    fin_embed.add_field(name="Rank", value=fin[2])
    fin_embed.add_field(name="Total fins", value=f"{player[1]}/225")
    fin_embed.add_field(name="\u200B", value="\u200B")  # newline
    fin_embed.add_field(name="Date", value=f"<t:{int(fin[3])}:f>")
    fin_embed.set_footer(text=f"Bot by djinn")
    return fin_embed
