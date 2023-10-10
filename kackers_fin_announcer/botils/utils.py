import json
import logging
from datetime import datetime
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


def _fins2tuple(fins: dict):
    """Convert json finish data to tuples"""
    ret = []
    for map, data in fins.items():
        tmp = (map,) + tuple(data.values())
        ret.append(tmp)
    return ret

# TODO: now this is dumb, surely there is a better way
def _fins2updatecreate(fins: dict, player_id: int):
    """Convert json finish data to consumable tuples for update_or_create_finishes()"""
    ret = []
    for map, data in fins.items():
        tmp = (map,) + tuple(data.values()) + (player_id, data["date"], data["score"], data["date"], data["kacky_rank"], data["score"], data["kacky_rank"], data["date"])
        ret.append(tmp)
    return ret


def _score_to_string(score: int, delta: int) -> str:
    """Converts map score to a string with seconds representation."""
    diff = ""
    score_fmt = datetime.fromtimestamp(score / 1000.0).strftime("%M:%S.%f")[:-3]
    if delta != 0:
        diff = f"(-{delta / 1000.0:.3f})"
    return f"{score_fmt} {diff}"


def build_announce_embed(player: dict, fin: dict) -> discord.Embed:
    logger.debug("Building announce embed")
    is_new = fin["created_at"] == fin["updated_at"]
    fin_embed = discord.Embed(
        title=":checkered_flag: NEW FINISH :checkered_flag:" if is_new else ":fire: NEW PB :fire:",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        color=discord.Color.random(),
    )
    fin_embed.set_thumbnail(url=CFG.thumbnails.replace("MAPNR", fin["mapname"]))
    fin_embed.add_field(name="Player", value=player["username"])
    fin_embed.add_field(name="\u200B", value="\u200B")  # newline
    fin_embed.add_field(name="Map", value=f"#{fin['mapname']}")
    fin_embed.add_field(name="Time", value=_score_to_string(fin["score"], fin["score_delta"]))
    fin_embed.add_field(name="\u200B", value="\u200B")  # newline
    fin_embed.add_field(name="Rank", value=fin["rank"] if is_new else f"{fin['rank']}({fin['rank_delta']}.)")
    fin_embed.add_field(name="Total fins", value=player["fincount"])
    fin_embed.add_field(name="\u200B", value="\u200B")  # newline
    fin_embed.add_field(name="Date", value= f"<t:{int(datetime.timestamp(fin['date']))}:f>")
    fin_embed.set_footer(text=f"Bot by djinn")
    return fin_embed