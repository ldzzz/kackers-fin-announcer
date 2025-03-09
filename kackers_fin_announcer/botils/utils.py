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
    logger.info("Building announce embed")

    title = ":checkered_flag: NEW FINISH :checkered_flag:"
    try:
        title = determine_embed_title(player, fin)
    except Exception as e:
        logger.info("Failed to determine title: ", e)

    fin_embed = discord.Embed(
        title=(title),
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        color=discord.Color.random(),
    )
    fin_embed.set_thumbnail(url=CFG.thumbnails.replace("MAPNR", fin["mapnr"]))
    fin_embed.add_field(name="Player", value=player["username"])
    fin_embed.add_field(name="\u200B", value="\u200B")  # newline
    fin_embed.add_field(name="Map", value=f"#{fin['mapnr']}")
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

    #if (f"{fin['kacky_rank']}") fin_embed.add_field("<@&>")

    fin_embed.set_footer(text=f"Bot by djinn and ultra")
    return fin_embed

def determine_embed_title(player: dict, fin: dict):
    """
    Returns the correct title for the embed based on the parameters.

    It checks for wr's, pbs with rank <= 5, hunting ranks achieved, and new finishes
    """

    edition_count = int(CFG.mappack_count / 75)
    ranks_numbers = [edition_count * 10, edition_count * 25, edition_count * 50, edition_count * 65, edition_count * 75]
    ranks_title = [
        ":PepegaClown: NEW PLASTIC RANK :PepegaClown:"
        ":Pepeg: NEW BRONZE RANK :Pepeg:"
        ":Pepega: NEW SILVER RANK :Pepega:"
        ":PepegaDriving: NEW GOLD RANK :PepegaDriving:"
        ":Nerdge: NEW KACKY RANK :Nerdge:" 
    ]

    if "score_delta" in fin.keys():
        if fin['kacky_rank'] == 1:
            return ":crown: NEW WORLD RECORD :crown:"
        else:
            return ":fire: NEW TOP 5 :fire:"
        
    for i in range(len(ranks_numbers)):
        if player["fincount"] == ranks_numbers[i]:
            return ranks_title[i]
        
    return ":checkered_flag: NEW FINISH :checkered_flag:"

def get_latest_finishes(old, new):
    """Gets latest finishes.

    Args:
        old         (dict): Current player finishes
        new         (dict): Fetched player finishes

    Returns:
        list: list of new and PB finishes
    """
    ret = []
    for mapnr, mapdata in new.items():
        # add new finish found
        if mapnr not in list(old.keys()):
            mapdata["mapnr"] = mapnr
            ret.append(mapdata)
        # add new PB if <= CFG.pb_limit and fresh
        elif (
            mapdata["date"] > old[mapnr]["date"]
            and mapdata["score"] < old[mapnr]["score"]
            and mapdata["kacky_rank"] <= CFG.pb_limit
        ):
            # prepare PB data
            mapdata["mapnr"] = mapnr
            score_delta = old[mapnr]["score"] - mapdata["score"]
            # detect abnormalities (e.g. v2 map issues)
            if score_delta > 0:
                mapdata["score_delta"] = score_delta
                mapdata["rank_delta"] = mapdata["kacky_rank"] - old[mapnr]["kacky_rank"]
                ret.append(mapdata)
            else:
                # if abnormality detected, do nothing, report error
                logger.error(
                    f"Abnormality detected for {mapnr}\nOLD: {old[mapnr]}\nNEW: {mapdata}"
                )
    return ret
