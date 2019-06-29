import abc
import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class KeyFingerprint:
    length: int
    hash: str
    comment: str
    key_type: str

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, KeyFingerprint):
            return NotImplemented

        return (
            self.length == other.length
            and self.hash == other.hash
            and self.key_type == other.key_type
        )

    def __hash__(self) -> int:
        return hash(self.length) + hash(self.hash) + hash(self.key_type)

    @classmethod
    def from_str(cls, s: str) -> "KeyFingerprint":
        length, hash, comment, key_type = s.split()
        return KeyFingerprint(
            length=int(length),
            hash=hash,
            comment=comment,
            key_type=key_type.strip("(").strip(")"),
        )

    def to_str(self) -> str:
        return f"{self.length} {self.hash} {self.comment} ({self.key_type})"


class AbstractFingerprintGenerator(abc.ABC):
    @abc.abstractmethod
    def for_path(self, path: Path) -> KeyFingerprint:
        ...


class MD5FingerprintGenerator(AbstractFingerprintGenerator):
    def for_path(self, path: Path) -> KeyFingerprint:
        md5 = hashlib.md5()
        md5.update(path.read_bytes())
        hex = str(md5.hexdigest())
        return KeyFingerprint(
            length=len(hex), hash=hex, comment="some-key", key_type="md5"
        )


class SSHKeyGenFingerprintGenerator(AbstractFingerprintGenerator):
    def __init__(self, executable_name: str = "ssh-keygen") -> None:
        self.__executable_name = executable_name

    def for_path(self, path: Path) -> KeyFingerprint:
        output = subprocess.check_output(
            [self.__executable_name, "-l", "-f", path], encoding="utf-8"
        )
        return KeyFingerprint.from_str(output.strip())
