import abc
import json
from pathlib import Path
from typing import Dict, List, Tuple

from op_askpass.configuration import get_configuration_directory


class AbstractKeyStore(abc.ABC):
    @abc.abstractmethod
    def add_fingerprint(self, fingerprint: str, onepass_uid: str) -> None:
        ...

    @abc.abstractmethod
    def delete_fingerprint(self, fingerprint: str) -> None:
        ...

    @abc.abstractmethod
    def get_onepass_uid(self, fingerprint: str) -> str:
        ...

    @abc.abstractmethod
    def items(self) -> List[Tuple[str, str]]: ...


class MemoryKeyStore(AbstractKeyStore):
    def delete_fingerprint(self, fingerprint: str) -> None:
        self.__store.pop(fingerprint, None)

    def items(self) -> List[Tuple[str, str]]:
        return list(self.__store.items())

    def get_onepass_uid(self, fingerprint: str) -> str:
        return self.__store[fingerprint]

    def __init__(self) -> None:
        self.__store: Dict[str, str] = {}

    def add_fingerprint(self, fingerprint: str, onepass_uid: str) -> None:
        self.__store[fingerprint] = onepass_uid


class FileKeyStore(AbstractKeyStore):
    def delete_fingerprint(self, fingerprint: str) -> None:
        contents = self.__read_contents(self.__file_path)
        contents.pop(fingerprint, None)
        self.__save_contents(file_path=self.__file_path, contents=contents)

    def items(self) -> List[Tuple[str, str]]:
        return list(self.__read_contents(self.__file_path).items())

    def __init__(self, file_path: Path) -> None:
        self.__file_path = file_path

    @staticmethod
    def __read_contents(file_path: Path) -> Dict[str, str]:
        try:
            return json.loads(file_path.read_text(encoding="utf-8"))

        except IOError:
            return {}

    @staticmethod
    def __save_contents(file_path: Path, contents: Dict[str, str]) -> None:
        file_path.write_text(json.dumps(contents), encoding="utf-8")

    def add_fingerprint(self, fingerprint: str, onepass_uid: str) -> None:
        contents = self.__read_contents(self.__file_path)
        contents[fingerprint] = onepass_uid
        self.__save_contents(file_path=self.__file_path, contents=contents)

    def get_onepass_uid(self, fingerprint: str) -> str:
        return self.__read_contents(self.__file_path)[fingerprint]


def get_default_key_store() -> AbstractKeyStore:
    return FileKeyStore(file_path=get_configuration_directory() / ".op-askpass.json")
