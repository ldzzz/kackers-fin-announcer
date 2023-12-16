import shelve

from botils.utils import CFG, _get_module_logger

logger = _get_module_logger(__name__)


def get_all_players() -> list:
    """Get a list of all players

    Returns:
        list: list of all player usernames
    """
    with shelve.open(filename=CFG.storage) as std:
        return list(std.keys())


def get_all_data() -> dict:
    """Get all player data from a shelf

    Returns:
        list: list of all registered players and their finishes
    """
    data = {}
    with shelve.open(filename=CFG.storage) as std:
        for player in list(std.keys()):
            data[player] = std[player]
    return data


def add_or_update_player(username: str, fins: dict) -> None:
    """Adds or updates player data

    Args:
        username (str): player username
        fins (dict): dict of finishes and their metadata
    """
    with shelve.open(filename=CFG.storage, writeback=True) as std:
        std[username] = fins


def delete_player(username: str) -> None:
    """Delete player by their username. If player doesn't exist this method silently fails

    Args:
        username (str): Player username to delete
    """
    with shelve.open(filename=CFG.storage, writeback=True) as std:
        try:
            del std[username]
        except KeyError:
            logger.info(f"No player with username {username} in storage")


def update_username(old_name: str, new_name: str) -> None:
    """Updates old_name with new_name

    Args:
        old_name (str): Old player username
        new_name (str): New player username
    """
    with shelve.open(filename=CFG.storage, writeback=True) as std:
        try:
            std[new_name] = std[old_name]
            del std[old_name]
        except KeyError:
            logger.info(f"No player with username {old_name} in storage")


# TODO: add possibility to change config values and save them to the shelve
# TODO: add possibility to load config values on start from shelve if they are present
