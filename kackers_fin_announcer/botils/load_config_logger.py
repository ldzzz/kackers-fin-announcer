import json
import logging

from pathlib import Path

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