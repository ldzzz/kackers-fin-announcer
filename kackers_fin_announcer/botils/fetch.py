import requests
from botils.utils import CFG, _get_module_logger

logger = _get_module_logger(__name__)


def fetch_player_finishes(player: str) -> dict:
    """Fetch player fins and convert to list of tuples"""
    url = CFG.api.replace("USER", player)
    logger.info(f"Fetching data for player: {player} via {url}")
    try:
        data = requests.get(
            url=url,
            headers={
                "User-Agent": "finbot 0.69",
                "X-ApiKey": CFG.api_token,
            },
            timeout=1,
        )
        return data.json()
    except Exception:
        logger.error("Kacky API not reachable?")
        return {}
