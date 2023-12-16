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


def _create_embed(title: str, data: dict = None) -> discord.Embed:
    mbed = discord.Embed(title=title)
    if data is not None:
        for k, v in data.items():
            mbed.add_field(name=k, value=v)
    return mbed


def _score_to_string(score: int, delta: int) -> str:
    """Converts map score to a string with seconds representation."""
    score_fmt = datetime.fromtimestamp(score / 1000.0).strftime("%M:%S.%f")[:-3]
    diff = f"(-{delta / 1000.0:.3f})" if delta else ""
    return f"{score_fmt} {diff}"


def build_announce_embed(player: dict, fin: dict) -> discord.Embed:
    logger.debug("Building announce embed")
    fin_embed = discord.Embed(
        title=":checkered_flag: NEW FINISH :checkered_flag:"
        if "score_delta" not in fin.keys()
        else ":fire: NEW TOP 5 :fire:",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        color=discord.Color.random(),
    )
    fin_embed.set_thumbnail(url=CFG.thumbnails.replace("MAPNR", fin["mapname"]))
    fin_embed.add_field(name="Player", value=player["username"])
    fin_embed.add_field(name="\u200B", value="\u200B")  # newline
    fin_embed.add_field(name="Map", value=f"#{fin['mapname']}")
    fin_embed.add_field(
        name="Time", value=_score_to_string(fin["score"], fin.get("score_delta", None))
    )
    fin_embed.add_field(name="\u200B", value="\u200B")  # newline
    fin_embed.add_field(
        name="Rank",
        value=f"{fin['kacky_rank']}"
        + (f"({fin['rank_delta']})" if "rank_delta" in fin.keys() else ""),
    )
    fin_embed.add_field(name="Total fins", value=player["fincount"])
    fin_embed.add_field(name="\u200B", value="\u200B")  # newline
    fin_embed.add_field(name="Date", value=f"<t:{int(fin['date'])}:f>")
    fin_embed.set_footer(text=f"Bot by djinn")
    return fin_embed


def get_latest_finishes(old, new, timestamp):
    """Gets latest finishes based on timestamp and interval of the checks.

    Args:
        old         (dict): Current player finishes
        new         (dict): Fetched player finishes
        timestamp   (datetime): Timestamp of the scheduled fetched start

    Returns:
        list: list of new and PB finishes
    """
    latest = list(
        filter(
            lambda k: new[k]["date"] >= (timestamp - CFG.interval),
            new,
        )
    )
    ret = []
    for mapname in latest:
        if mapname not in list(old.keys()):
            # add new finish found
            new[mapname]["mapname"] = mapname
            ret.append(new[mapname])
        elif new[mapname]["kacky_rank"] <= CFG.pb_limit:
            # prepare PB data
            new[mapname]["mapname"] = mapname
            score_delta = old[mapname]["score"] - new[mapname]["score"]
            # detect abnormalities
            if score_delta < 0:
                # if abnormality detected, treat it as a new fin (probably a v2 of a map)
                logger.error(
                    f"Abnormality detected for {mapname}\nOLD: {old[mapname]}\nNEW: {new[mapname]}"
                )
                ret.append(new[mapname])
                continue
            new[mapname]["score_delta"] = score_delta
            new[mapname]["rank_delta"] = (
                new[mapname]["kacky_rank"] - old[mapname]["kacky_rank"]
            )
            ret.append(new[mapname])
    return ret
