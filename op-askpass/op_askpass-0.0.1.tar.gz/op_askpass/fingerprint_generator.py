import abc
import hashlib
import subprocess
from pathlib import Path


class AbstractFingerprintGenerator(abc.ABC):
    @abc.abstractmethod
    def for_path(self, path: Path) -> str:
        ...


class MD5FingerprintGenerator(AbstractFingerprintGenerator):
    def for_path(self, path: Path) -> str:
        md5 = hashlib.md5()
        md5.update(path.read_bytes())
        return str(md5.hexdigest())


class SSHKeyGenFingerprintGenerator(AbstractFingerprintGenerator):
    def __init__(self, executable_name: str = "ssh-keygen") -> None:
        self.__executable_name = executable_name

    def for_path(self, path: Path) -> str:
        output = subprocess.check_output([self.__executable_name, "-l", "-f", path], encoding="utf-8")
        return output.strip()
