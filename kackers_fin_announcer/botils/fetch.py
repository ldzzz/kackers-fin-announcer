import requests
from botils.utils import CFG, _get_module_logger

logger = _get_module_logger(__name__)

"""
@tasks.loop(seconds=10)
async def fetch_fins(members):

@fetch_fins.before_loop
async def before():
  await client.wait_until_ready()

fetch_fins.start() #deplaced outside of the function
"""


def fetch_player_fins(player: str) -> dict:
    url = CFG.api.endpoint.replace("USER", player) + CFG.api.edition
    logger.info(f"Fetching data for player: {player} via {url}")
    data = requests.get(url).json()
    return data
