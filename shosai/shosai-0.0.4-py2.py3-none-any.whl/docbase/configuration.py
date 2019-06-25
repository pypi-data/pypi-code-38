import sys
import json
import logging
import os.path
from ..langhelpers import reify
from . import structure
logger = logging.getLogger(__name__)


def init(path: str) -> None:
    api_token: str = "<from https://help.docbase.io/posts/45703#%E3%82%A2%E3%82%AF%E3%82%BB%E3%82%B9%E3%83%88%E3%83%BC%E3%82%AF%E3%83%B3>"
    d: structure.ProfileDict = {
        "teamname": "<team>",
        "token": api_token,
        "username": "<user>",
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    logger.info("write: %s", path)
    with open(path, "w") as wf:
        json.dump({"docbase": d}, wf, indent=2)


def load(config_path: str, *, init=init):
    if not os.path.exists(config_path):
        print(f"{config_path} is not found, generated. please setting this file.", file=sys.stderr)
        init(config_path)
        sys.exit(1)

    logger.info("read: %s", config_path)
    with open(config_path) as rf:
        config = json.load(rf)
    return config["docbase"]


class Profile:
    data: structure.ProfileDict

    def __init__(self, config_path: str) -> None:
        self.data = load(config_path)

    # todo: remove?
    @reify
    def token(self) -> str:
        return self.data["token"]

    @reify
    def username(self) -> str:
        return self.data["username"]

    @reify
    def teamname(self) -> str:
        return self.data["teamname"]
