import json
from datetime import datetime

import botils.config
import discord
from botils.load_config_logger import get_module_logger
from botils.nadeoAPI import get_top_two

logger = get_module_logger(__name__)

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


def build_announce_embed(player: dict, fin: dict, isKr: bool) -> discord.Embed:
    logger.info("Building announce embed")

    title = ":checkered_flag: NEW FINISH :checkered_flag:"
    try:
        title = determine_embed_title(player, fin)
    except Exception as e:
        logger.info("Failed to determine title: ", e)

    thumbnail_url = ""
    if isKr:
        thumbnail_url = botils.config.CFG.BOT["bot"]["thumbnails_kr"].replace("MAPNR", str(fin["number"]))
    else: 
        thumbnail_url = botils.config.CFG.BOT["bot"]["thumbnails_kx"]

    fin_embed = discord.Embed(
        title=(title),
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        color=discord.Color.random(),
    )
    fin_embed.set_thumbnail(url=thumbnail_url)
    fin_embed.add_field(name="Player", value=player["username"])
    fin_embed.add_field(name="\u200B", value="\u200B")  # newline
    fin_embed.add_field(name="Map", value=f"#{fin['number']}")
    fin_embed.add_field(
        name="Time", value=_score_to_string(fin["score"], fin.get("score_delta", None))
    )
    fin_embed.add_field(name="\u200B", value="\u200B")  # newline
    # TODO: this will also need updating to be nicer and work with PBs, WRs and stuff
    fin_embed.add_field(name="Total fins", value=player["fincount"])
    #fin_embed.add_field(name="\u200B", value="\u200B")  # newline
    date = f"{parse_ts(fin['lastImprovedAt'])}"
    fin_embed.add_field(name="Date", value=date[:-6])
    #fin_embed.add_field(
    #    name="Rank",
    #    value=f"{fin['kacky_rank']}"
    #    + (f"({fin['rank_delta']})" if "rank_delta" in fin.keys() else ""),
    #)

    #if (fin['kacky_rank'] == 1):
    #    offlineTopTwo = get_top_two(fin['mapnr'])

    #    if offlineTopTwo[0] == fin['score']:
    #        fin_embed.add_field(name="Old WR", value=_score_to_string(offlineTopTwo[1], offlineTopTwo[1] - offlineTopTwo[0]))
    #        fin_embed.add_field(name="\u200B", value="\u200B")
    #        fin_embed.add_field(name="\u200B", value="\u200B")
    #    else:
    #        fin_embed.add_field(name="Total fins", value=player["fincount"])
    #        fin_embed.add_field(name="\u200B", value="\u200B")  # newline
    #        fin_embed.add_field(name="Date", value=f"<t:{int(fin['date'])}:f>")
    #else:
    #    fin_embed.add_field(name="Total fins", value=player["fincount"])
    #    fin_embed.add_field(name="\u200B", value="\u200B")  # newline
    #    fin_embed.add_field(name="Date", value=f"<t:{int(fin['date'])}:f>")

#    if (fin['kacky_rank'] == 1): 
#        fin_embed.add_field(name="WR-Ping", value="<@&1349723580203536527>")

    fin_embed.set_footer(text=f"Bot by djinn and ultra")
    logger.info("Built announce embed")
    return fin_embed

def determine_embed_title(player: dict, fin: dict):
    """
    Returns the correct title for the embed based on the parameters.

    It checks for wr's, pbs with rank <= 5, hunting ranks achieved, and new finishes
    """
    # TODO: this will need to be rewritten
    #edition_count = int(int(CFG[CFG["bot"]["mode"]]["mappack_count"]) // 75)
    #ranks_numbers = [edition_count * 10, edition_count * 25, edition_count * 50, edition_count * 65, edition_count * 75]
    #ranks_title = [
    #    "<:PepegaClown:1301186994717724745> NEW PLASTIC RANK <:PepegaClown:1301186994717724745>",
    #    "<:Pepeg:1301185040272719985> NEW BRONZE RANK <:Pepeg:1301185040272719985>",
    #    "<:Pepega:1301185111399731242> NEW SILVER RANK <:Pepega:1301185111399731242>",
    #    "<:PepegaDriving:1301185137282650113> NEW GOLD RANK <:PepegaDriving:1301185137282650113>",
    #    "<:Nerdge:1301196656309567558> NEW KACKY RANK <:Nerdge:1301196656309567558>" 
    #]

    #if "score_delta" in fin.keys():
    #    if fin['kacky_rank'] == 1:
    #        offlineTopTwo = get_top_two(fin['mapnr'])
    #        if offlineTopTwo[0] == fin['score']:
    #            return ":crown: NEW WORLD RECORD :crown:"
    #        else:
    #            return ":fire: NEW TOP 5 :fire:"
    #    else:
    #        return ":fire: NEW TOP 5 :fire:"
        
    #for i in range(len(ranks_numbers)):
    #    if player["fincount"] == ranks_numbers[i]:
    #        return ranks_title[i]
        
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
    old_dict = {str(e["number"]): e for e in old}
    for entry in new:
        num = entry["number"]
        if str(num) not in old_dict.keys(): # Completely new finish
            ret.append(entry)
    # TODO: somehow gotta check if PB worthy announcing or not - the new API doesn't return "rank" anymore - so we probably have to check the map lb or something
    # TODO: careful for event as this is sent to be appended to current finishes of a player
    return ret


def parse_teams(teams: bytes) -> list:
    teams = json.loads(teams.decode().strip())
    print(teams)
    return teams


def filter_duplicates(records: list) -> list:
    latest_entries = {}
    for entry in records:
        num = entry["number"]
        if num not in latest_entries:
            latest_entries[num] = entry
        else:
            if parse_ts(entry["lastImprovedAt"]) > parse_ts(latest_entries[num]["lastImprovedAt"]):
                latest_entries[num] = entry
    return list(latest_entries.values())


# Convert ISO timestamp to datetime
def parse_ts(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))