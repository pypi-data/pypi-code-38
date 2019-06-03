import json

from .base import ConfigParserBase


class JSONConfigParser(ConfigParserBase):
    __slots__ = ["content"]

    def parse(self, content: str) -> dict:
        """Parse JSON file and return dict.

        :param content: content from JSON file
        :type content: str
        :raises ValueError: if content is empty
        :return: parsed config dict
        :rtype: dict
        """
        content = super().parse(content)

        if content == "":
            raise ValueError("Cannot parse empty configuration")

        with self.statsd.get_timer().time("parse_time"):
            config = json.loads(content)
        self.statsd.get_counter().increment("parse")
        return config
