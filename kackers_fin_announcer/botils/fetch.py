import requests
from botils.utils import CFG, _get_module_logger, _cleanup_fins

logger = _get_module_logger(__name__)


def fetch_player_fins(player: str) -> list:
    """Fetch player fins and convert to list of tuples"""
    url = CFG.api.replace("USER", player)
    logger.info(f"Fetching data for player: {player} via {url}")
    data = requests.get(url).json()
    cleaned_data = _cleanup_fins(data)
    return cleaned_data
