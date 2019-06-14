import csv
from pathlib import PurePath
from typing import Dict

from src.environment import ORIGINAL, TRANSCODED


class _CP932Conversion:
    """
    A SingleTon class which provides transcoding service to cp932-incompatible characters
    """
    instance = None

    def __init__(self) -> None:
        self._character_dict: Dict[str, str] = self._dict_data_reader()

    def convert(self, char: str) -> str:
        """
        :param char: A single Japanese character
        :return: A cp932-friendly version of the given character
        """
        return self._character_dict[char]

    @staticmethod
    def _dict_data_reader() -> Dict[str, str]:
        conf_file_path = str(PurePath(str(PurePath(__file__).parent), "cp932.conf"))
        character_dict: Dict[str, str] = {}
        with open(conf_file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                character_dict[row[ORIGINAL]] = row[TRANSCODED]

        return character_dict


def CP932Conversion() -> _CP932Conversion:
    if _CP932Conversion.instance is None:
        _CP932Conversion.instance = _CP932Conversion()

    return _CP932Conversion.instance
