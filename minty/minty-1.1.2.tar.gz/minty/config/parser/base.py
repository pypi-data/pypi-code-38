from abc import ABC, abstractmethod

from ... import Base


class ConfigParserBase(ABC, Base):
    @abstractmethod
    def parse(self, content: str) -> str:
        """Parse configuration content.

        Method is called in child classes `super().parse(content)` to make sure
        we can implement generic parsing behaviour if necessary.

        :param content: contents of the configuration file to parse
        :type content: str
        :return: the "content" parameter, unchanged
        :rtype: str
        """
        return content
