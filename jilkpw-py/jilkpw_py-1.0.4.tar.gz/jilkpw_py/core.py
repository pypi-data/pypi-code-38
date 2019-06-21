"""
core.py contains all of the basic utilities of this wrapper
"""

import requests
from jilkpw_py.error_catch import ResponseErrors


class JilkpwWrapper:
    api_endpoint = "https://jilk.pw/api/v1.0/public"

    def find(self, guild_id: int):
        """
        Gets the Jilk.pw listing dict from the given Guild ID
        """

        resp = requests.get(
            f"{self.api_endpoint}specific",
            params={"guild_id": guild_id}
        )

        ResponseErrors(resp.status_code)

        return resp.json()["details"]

    def all(self):
        """
        Gets all Jilk.pw listings
        """

        resp = requests.get(
            f"{self.api_endpoint}all"
        )

        ResponseErrors(resp.status_code)

        return resp.json()["details"]
