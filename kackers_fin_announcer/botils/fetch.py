import requests
from botils.load_config_logger import CFG, logger


def fetch_player_finishes(player: str, pid: int) -> list:
    """Fetch player fins and return it as a dictionary"""
    url = CFG[CFG["bot"]["mode"]]["api"].replace("PID", str(pid))
    logger.info(f"Fetching data for player: {player} via {url}")
    try:
        data = requests.get(
            url=url,
            headers={"User-Agent": "djinn-finbot 0.69"},
            timeout=5,
        )
        ret = data.json()["records"]
        return ret
    except Exception as e:
        logger.error("Kacky API not reachable or json not serializable?")
        logger.error(e)
        return {}
