import abc
import os
import subprocess
from pathlib import Path
from typing import List, Set

from op_askpass.fingerprint_generator import (
    AbstractFingerprintGenerator,
    MD5FingerprintGenerator,
    SSHKeyGenFingerprintGenerator,
    KeyFingerprint,
)


class AbstractKeyLoader(abc.ABC):
    @abc.abstractmethod
    def list_loaded_keys(self) -> List[KeyFingerprint]:
        ...

    @abc.abstractmethod
    def load_key(
        self, key_path: Path, op_domain: str, op_session_key: str, op_uid: str
    ) -> None:
        ...

    @abc.abstractmethod
    def get_fingerprint_generator(self) -> AbstractFingerprintGenerator:
        ...


class MemoryKeyLoader(AbstractKeyLoader):
    def get_fingerprint_generator(self) -> AbstractFingerprintGenerator:
        return MD5FingerprintGenerator()

    def __init__(self) -> None:
        self.__keys: Set[KeyFingerprint] = set()

    def load_key(
        self, key_path: Path, op_domain: str, op_session_key: str, op_uid: str
    ) -> None:
        self.__keys.add(self.get_fingerprint_generator().for_path(key_path))

    def list_loaded_keys(self) -> List[KeyFingerprint]:
        return list(self.__keys)


class SSHKeyLoader(AbstractKeyLoader):
    def get_fingerprint_generator(self) -> AbstractFingerprintGenerator:
        return SSHKeyGenFingerprintGenerator()

    def list_loaded_keys(self) -> List[KeyFingerprint]:
        output: str = subprocess.check_output(["ssh-add", "-l"], encoding="utf-8")
        return [KeyFingerprint.from_str(s) for s in output.splitlines()]

    def load_key(
        self, key_path: Path, op_domain: str, op_session_key: str, op_uid: str
    ) -> None:
        env = {**os.environ, f"OP_SESSION_{op_domain}": op_session_key}

        subprocess.check_call(
            ["ssh-add", str(key_path)],
            env={
                **env,
                "OP_ASKPASS_ITEM_NAME": op_uid,
                "SSH_ASKPASS": "op-askpass-get-password",
            },
            stdin=subprocess.DEVNULL,
        )
