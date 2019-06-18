import json
import random
from os import urandom, path
from binascii import hexlify
import requests
from typing import Tuple, Any

DATASET = requests.get("https://pastebin.com/raw/ZAQ2CZcv").json()


def get_object() -> str:
    object_type = random.choice(list(DATASET["objects"].keys()))

    return random.choice(DATASET["objects"][object_type]).capitalize()


def get_property() -> str:
    property_type = random.choice(list(DATASET["properties"].keys()))

    return random.choice(DATASET["properties"][property_type])


def get_version_name(seed=None) -> Tuple[str, Any]:
    if not seed:
        seed: str = hexlify(urandom(4)).decode().upper()

    random.seed(seed)

    return f"{get_property()} {get_object()}", seed

