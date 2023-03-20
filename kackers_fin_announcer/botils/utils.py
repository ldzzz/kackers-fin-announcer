import json
import logging
from datetime import datetime, timedelta
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


def _get_new_fins(fins: list):
    """Get fins by timestamp"""
    last12hr_timestamp = (datetime.now() - timedelta(hours=12)).timestamp()
    new_fins = []
    for fin in fins:
        if fin[3] >= last12hr_timestamp:
            new_fins.append(fin)
    return new_fins


# TODO: get only new fins by timestamp, and here sort them out
def get_updated_fins(fetched_fins: list, db_fins: dict):
    """For given player get new fins/PBs."""
    new_fins = []
    pb_fins = []
    updated_fins = _get_new_fins(fetched_fins)
    for m in updated_fins:
        dbmap = db_fins.get(m[0], None)
        if dbmap is not None:  # pb
            if m[3] > dbmap["date"] and m[1] < dbmap["score"]:
                delta = dbmap["score"] - m[1]
                pb_fins.append(
                    (tuple(dbmap.values())[::-1], (delta,) + m[::-1])
                )  # old, new
        else:  # new fin
            new_fins.append(m)

    return new_fins, pb_fins


def _score_to_string(score: int, delta: int = None) -> str:
    """Converts map score to a string with seconds representation."""
    diff = ""
    score_fmt = datetime.fromtimestamp(score / 1000.0).strftime("%M:%S.%f")[:-3]
    if delta:
        diff = f" (-{delta / 1000.0:.3f})"
    return f"{score_fmt} {diff}"


def build_announce_embed(player: tuple, fin: tuple) -> discord.Embed:
    logger.debug("Building announce embed")
    if len(fin) == 2:
        edata = {
            "title": ":fire: NEW PB :fire:",
            "map": fin[1][-1],
            "username": player[0],
            "time": _score_to_string(fin[1][3], fin[1][0]),
            "rank": f"{fin[1][2]} (-{fin[0][2] - fin[1][2]}.)",
            "total_fins": f"{player[1]}/{CFG.mappack_count}",
            "date": f"<t:{int(fin[1][1])}:f>",
        }
    else:
        edata = {
            "title": ":checkered_flag: NEW FINISH :checkered_flag:",
            "map": fin[0],
            "username": player[0],
            "time": _score_to_string(fin[1], None),
            "rank": fin[2],
            "total_fins": f"{player[1]}/{CFG.mappack_count}",
            "date": f"<t:{int(fin[3])}:f>",
        }
    fin_embed = discord.Embed(
        title=edata["title"],
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        color=discord.Color.random(),
    )
    fin_embed.set_thumbnail(
        url=CFG.thumbnails.replace("MAPNR", edata["map"].split()[0])
    )
    fin_embed.add_field(name="Player", value=edata["username"])
    fin_embed.add_field(name="\u200B", value="\u200B")  # newline
    fin_embed.add_field(name="Map", value=f"#{edata['map']}")
    fin_embed.add_field(name="Time", value=edata["time"])
    fin_embed.add_field(name="\u200B", value="\u200B")  # newline
    fin_embed.add_field(name="Rank", value=edata["rank"])
    fin_embed.add_field(name="Total fins", value=edata["total_fins"])
    fin_embed.add_field(name="\u200B", value="\u200B")  # newline
    fin_embed.add_field(name="Date", value=edata["date"])
    fin_embed.set_footer(text=f"Bot by djinn")
    return fin_embed
