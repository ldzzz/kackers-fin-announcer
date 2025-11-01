import json
import logging
import sys
from pathlib import Path

import botils.config


def get_module_logger(mod_name: str) -> logging.Logger:
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


logger = get_module_logger(__name__)


def _load_default_config():
    if len(sys.argv) != 3:
        logger.error("Please provide fin storage and bot cfg paths")
        exit(-1)
    with open(Path.cwd() / sys.argv[1], "r") as fp:
        botils.config.CFG.BOT = json.load(fp)
    logger.info(f"DEFAULT CFG loaded from {sys.argv[1]}")

def _load_secrets():
    if len(sys.argv) != 3:
        logger.error("Please provide fin storage and bot cfg paths")
        exit(-1)
    with open(Path.cwd() / sys.argv[2], "r") as fp:
        botils.config.CFG.SECRETS = json.load(fp)
        logger.info(f"SECRETS loaded from {sys.argv[2]}")