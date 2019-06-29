import abc
import hashlib
from pathlib import Path

import pytest

from op_askpass.fingerprint_generator import (
    AbstractFingerprintGenerator,
    MD5FingerprintGenerator,
    SSHKeyGenFingerprintGenerator,
    KeyFingerprint,
)

HERE = Path(__file__).parent


class AbstractFingerprintGeneratorTests(abc.ABC):
    @pytest.fixture
    def test_key_file_path(self, tmp_path: Path) -> Path:
        file_path = tmp_path / "yada.txt"
        file_path.write_bytes(b"xxx")
        return file_path

    def test_for_path_should_correctly_generate_fingerprint(
        self, test_key_file_path: Path
    ) -> None:
        generator = self.fingerprint_generator_factory()

        assert isinstance(generator.for_path(test_key_file_path), KeyFingerprint)

    @abc.abstractmethod
    def fingerprint_generator_factory(self) -> AbstractFingerprintGenerator:
        ...


class TestMD5FingerprintGenerator(AbstractFingerprintGeneratorTests):
    def fingerprint_generator_factory(self) -> AbstractFingerprintGenerator:
        return MD5FingerprintGenerator()

    def test_for_path_should_generate_md5_hash(self, tmp_path: Path) -> None:
        generator = self.fingerprint_generator_factory()
        file_path = tmp_path / "yada.txt"
        file_path.write_bytes(b"xxx")

        assert generator.for_path(file_path) == KeyFingerprint(
            length=32,
            hash="f561aaf6ef0bf14d4208bb46a4ccb3ad",
            comment="some-key",
            key_type="md5",
        )


class TestSSHKeyGenFingerprintGenerator(AbstractFingerprintGeneratorTests):
    @pytest.fixture
    def test_key_file_path(self) -> Path:
        return Path(HERE / "test_data" / "test_key.pub")

    def fingerprint_generator_factory(self) -> AbstractFingerprintGenerator:
        return SSHKeyGenFingerprintGenerator()

    def test_for_path_should_generate_correct_checksum(
        self, test_key_file_path: Path
    ) -> None:
        generator = self.fingerprint_generator_factory()

        assert generator.for_path(test_key_file_path) == KeyFingerprint.from_str(
            "2048 SHA256:IKJs9nCZuYQ2tND/G2kCM1/+ggJsWMnWn+iP7y4FXDc test@key (RSA)"
        )
