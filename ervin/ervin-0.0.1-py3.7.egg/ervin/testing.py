from pathlib import Path
import logging
from ervin.ervin_utils import get_config

CONFIG = get_config()

logging.basicConfig(filename="out.log", level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(f"{__name__}::{Path(__file__).stem}")


def run():
    logger.info("Test2")
