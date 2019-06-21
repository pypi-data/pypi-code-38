import json
import copy
from types import SimpleNamespace
import motor.motor_asyncio


def defaultSettings():
    return {
        "db": {
            "url": "localhost:27017",
            "name": "test",
        },
        "corsOrigins": [
            "http://localhost:3000",
            # "http://localhost:8080",
        ],
        "jwtKey": "onetwothree",
    }


def parseConfig(filename="config.json"):
    settings = copy.deepcopy(defaultSettings())
    if filename:
        settings.update(json.loads(open(filename).read()))

    return settings


def connectToDB(settings):
    client = motor.motor_asyncio.AsyncIOMotorClient(
        settings["db"]["url"],
        tz_aware=True,
    )
    settings["db"] = client[settings["db"]["name"]]
    return settings
