import shelve

from botils.load_config_logger import CFG, SECRETS, logger


def get_all_players() -> list:
    """Get a list of all players

    Returns:
        list: list of all player usernames
    """
    with shelve.open(filename=SECRETS["storage"]) as std:
        return list(std.keys())


def get_all_data() -> dict:
    """Get all player data from a shelf

    Returns:
        list: list of all registered players and their finishes
    """
    data = {}
    with shelve.open(filename=SECRETS["storage"]) as std:
        for player in list(std.keys()):
            data[player] = std[player]
    return data


def add_or_update_player(username: str, pid: int, fins: dict) -> None:
    """Adds or updates player data

    Args:
        username (str): player username
        pid (int): player id from kacky.gg
        fins (dict): dict of finishes and their metadata
    """
    with shelve.open(filename=SECRETS["storage"], writeback=True) as std:
        std[username] = {"id": pid, "finishes": fins}


def delete_player(username: str) -> None:
    """Delete player by their username. If player doesn't exist this method silently fails

    Args:
        username (str): Player username to delete
    """
    with shelve.open(filename=SECRETS["storage"], writeback=True) as std:
        try:
            del std[username]
        except KeyError:
            logger.info(f"No player with username {username} in storage")


# TODO: add possibility to change config values and save them to the shelve
# TODO: add possibility to load config values on start from shelve if they are present
def update_bot_config(bot: dict) -> None:
    """Adds or updates bot config data

    Args:
        bot (dict): All bot data needed
    """
    try:
        with shelve.open(filename=SECRETS["config"], writeback=True) as std:
            std["bot"] = bot
        update_CFG()
    except Exception as e:
        logger.error(f"Failed to update bot config: {e}")

def update_hunting_config(hunting: dict) -> None:
    """Adds or updates bot config data

    Args:
        hunting (dict): All hunting data needed
    """
    try:
        with shelve.open(filename=SECRETS["config"], writeback=True) as std:
            std["hunting"] = hunting
        update_CFG()
    except Exception as e:
        logger.error(f"Failed to update hunting config: {e}")

def update_event_config(event: dict) -> None:
    """Adds or updates bot config data

    Args:
        event (dict): All event data needed
    """
    try:
        with shelve.open(filename=SECRETS["config"], writeback=True) as std:
            std["event"] = event
        update_CFG()
    except Exception as e:
        logger.error(f"Failed to update event config: {e}")

def get_config() -> dict:
    """Gets saved config if it exists"""
    data = {}
    with shelve.open(filename=SECRETS["config"], writeback=True) as std:
        for cfg in list(std.keys()):
            data[cfg] = std[cfg]
    return data

def update_CFG() -> None:
    global CFG
    logger.info("Updating CFG")
    with shelve.open(filename=SECRETS["config"], writeback=True) as std:
        for cfg in list(std.keys()):
            CFG[cfg] = std[cfg]
