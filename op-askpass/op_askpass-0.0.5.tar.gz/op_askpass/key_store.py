import abc
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from op_askpass.configuration import get_configuration_directory
from op_askpass.fingerprint_generator import KeyFingerprint


@dataclass
class KeyEntry:
    key_path: Path
    onepass_uid: str


class AbstractKeyStore(abc.ABC):
    @abc.abstractmethod
    def add_fingerprint(
        self, fingerprint: KeyFingerprint, onepass_uid: str, key_path: Path
    ) -> None:
        ...

    @abc.abstractmethod
    def delete_fingerprint(self, fingerprint: KeyFingerprint) -> None:
        ...

    @abc.abstractmethod
    def get_key_entry(self, fingerprint: KeyFingerprint) -> KeyEntry:
        ...

    @abc.abstractmethod
    def items(self) -> List[Tuple[KeyFingerprint, KeyEntry]]:
        ...


class MemoryKeyStore(AbstractKeyStore):
    def delete_fingerprint(self, fingerprint: KeyFingerprint) -> None:
        self.__store.pop(fingerprint, None)

    def items(self) -> List[Tuple[KeyFingerprint, KeyEntry]]:
        return list(self.__store.items())

    def get_key_entry(self, fingerprint: KeyFingerprint) -> KeyEntry:
        return self.__store[fingerprint]

    def __init__(self) -> None:
        self.__store: Dict[KeyFingerprint, KeyEntry] = {}

    def add_fingerprint(
        self, fingerprint: KeyFingerprint, onepass_uid: str, key_path: Path
    ) -> None:
        self.__store[fingerprint] = KeyEntry(onepass_uid=onepass_uid, key_path=key_path)


class FileKeyStore(AbstractKeyStore):
    def delete_fingerprint(self, fingerprint: KeyFingerprint) -> None:
        contents = self.__read_contents(self.__file_path)
        contents.pop(fingerprint, None)
        self.__save_contents(file_path=self.__file_path, contents=contents)

    def items(self) -> List[Tuple[KeyFingerprint, KeyEntry]]:
        return list(self.__read_contents(self.__file_path).items())

    def __init__(self, file_path: Path) -> None:
        self.__file_path = file_path

    @staticmethod
    def __read_contents(file_path: Path) -> Dict[KeyFingerprint, KeyEntry]:
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            return {
                KeyFingerprint.from_str(k): KeyEntry(
                    onepass_uid=v["onepass_uid"], key_path=Path(v["key_path"])
                )
                for k, v in data.items()
            }

        except IOError:
            return {}

    @staticmethod
    def __save_contents(
        file_path: Path, contents: Dict[KeyFingerprint, KeyEntry]
    ) -> None:
        file_path.write_text(
            json.dumps(
                {
                    k.to_str(): {
                        "onepass_uid": v.onepass_uid,
                        "key_path": str(v.key_path),
                    }
                    for k, v in contents.items()
                }
            ),
            encoding="utf-8",
        )

    def add_fingerprint(
        self, fingerprint: KeyFingerprint, onepass_uid: str, key_path: Path
    ) -> None:
        contents = self.__read_contents(self.__file_path)
        contents[fingerprint] = KeyEntry(onepass_uid=onepass_uid, key_path=key_path)
        self.__save_contents(file_path=self.__file_path, contents=contents)

    def get_key_entry(self, fingerprint: KeyFingerprint) -> KeyEntry:
        return self.__read_contents(self.__file_path)[fingerprint]


def get_default_key_store() -> AbstractKeyStore:
    return FileKeyStore(file_path=get_configuration_directory() / "op-askpass.json")
