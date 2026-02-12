import botils.config
import requests
from botils.load_config_logger import get_module_logger
from botils.nadeoAPI import isReloaded

logger = get_module_logger(__name__)

def fetch_player_finishes(player: str, pid: int) -> list:
    """Fetch player fins and return it as a dictionary"""
    url = botils.config.CFG.BOT[botils.config.CFG.BOT["bot"]["mode"]]["api"].replace("PID", str(pid))
    logger.info(f"Fetching data for player: {player} via {url}")
    try:
        data = requests.get(
            url=url,
            headers={"User-Agent": "djinn-finbot 0.69"},
            timeout=5,
        )
        fins = data.json()["records"]
        krfins = []
        kxfins = []
        for fin in fins:
            if isReloaded(fin['mapUid']):
                krfins.append(fin)
            else:
                kxfins.append(fin)

        return [krfins, kxfins]
    
    except Exception as e:
        logger.error("Kacky API not reachable or json not serializable?")
        logger.error(e)
        return [{}, {}]
