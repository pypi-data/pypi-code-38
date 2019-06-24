import base64
import json
import logging
import os
from datetime import datetime

import requests
import xdg

logger = logging.getLogger(__name__)


class _TVDBClient:
    CONFIG_PATH = f"{xdg.XDG_CONFIG_HOME}/tv.config.json"

    def initialize(self):
        if os.path.exists(self.CONFIG_PATH):
            logger.warning(f"{self.CONFIG_PATH} already exists, not overwriting")
            return
        self.api_key = input(f"Please enter your API key from thetvdb.com: ")
        self.login()
        self.save()

    def load(self):
        logger.debug("Loading configuration from disk")
        try:
            with open(self.CONFIG_PATH) as file_:
                config = json.load(file_)
                self.api_key = config["api_key"]
                self._token = config["token"]
        except FileNotFoundError:
            print(
                f"Error: the configuration file does not exist. Please run the `init` "
                "subcommand."
            )
            exit(1)

    def save(self):
        logger.debug("Dumping configuration to disk")
        with open(self.CONFIG_PATH, "w") as file_:
            json.dump({"api_key": self.api_key, "token": self._token}, file_)

    @property
    def token(self):
        if not hasattr(self, "_token"):
            self.load()

        # Reauthenticate if the token has expired
        _, payload_encoded, _ = self._token.split(".")
        payload = json.loads(base64.b64decode(payload_encoded))
        expiry = datetime.fromtimestamp(payload["exp"])
        if datetime.now() >= expiry:
            logger.debug("Token has expired, re-authenticating")
            self.login()
            self.save()

        return self._token

    def login(self):
        logger.info("Authenticating with thetvdb api for JWT")
        response = requests.post(
            "https://api.thetvdb.com/login", json={"apikey": self.api_key}
        )
        response.raise_for_status()
        self._token = response.json()["token"]

    def query_series(self, series_id, language):
        logger.info(f"{series_id}: Querying series data")
        response = requests.get(
            f"https://api.thetvdb.com/series/{series_id}",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept-Language": language,
            },
        )
        response.raise_for_status()
        series = response.json()["data"]

        page = 1
        episodes = []
        while True:
            logger.info(f"{series_id}: Querying episode data (page {page})")
            response = requests.get(
                f"https://api.thetvdb.com/series/{series_id}/episodes",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Accept-Language": language,
                },
                params={"page": page},
            )
            response.raise_for_status()
            result = response.json()
            # Ignore specials with season 0
            episodes.extend([e for e in result["data"] if e["airedSeason"] != 0])
            if result["links"]["last"] == page:
                break
            page += 1
        return series, episodes

    def search(self, series_name):
        logger.info(f"Searching thetvdb for '{series_name}'")
        response = requests.get(
            f"https://api.thetvdb.com/search/series",
            headers={"Authorization": f"Bearer {self.token}"},
            params={"name": series_name},
        )
        response.raise_for_status()
        return response.json()["data"]


tvdb = _TVDBClient()
