import abc
import uuid
from pathlib import Path

import pytest

from op_askpass.fingerprint_generator import KeyFingerprint
from op_askpass.key_store import (
    AbstractKeyStore,
    MemoryKeyStore,
    FileKeyStore,
    KeyEntry,
)


class AbstractKeyStoreTests(abc.ABC):
    def test_add_key_fingerprint_should_correctly_add_fingerprint(self) -> None:
        key_store: AbstractKeyStore = self.key_store_factory()
        onepass_uid = "XXXXXX"
        fingerprint = KeyFingerprint(
            length=10, hash="SSSSSSSSS", comment="x", key_type="some"
        )
        path = Path("x")
        expected_entry = KeyEntry(onepass_uid=onepass_uid, key_path=path)

        key_store.add_fingerprint(
            fingerprint=fingerprint, onepass_uid=onepass_uid, key_path=path
        )

        assert key_store.get_key_entry(fingerprint=fingerprint) == expected_entry
        assert key_store.items() == [(fingerprint, expected_entry)]

    def test_delete_key_fingerprint_should_correctly_remove_a_fingerprint(self) -> None:
        key_store: AbstractKeyStore = self.key_store_factory()
        onepass_uid = "XXXXXX"
        fingerprint = KeyFingerprint(
            length=10, hash="SSSSSSSSS", comment="x", key_type="some"
        )
        path = Path("x")
        key_store.add_fingerprint(
            fingerprint=fingerprint, onepass_uid=onepass_uid, key_path=path
        )

        key_store.delete_fingerprint(fingerprint=fingerprint)

        with pytest.raises(KeyError, match=fingerprint.hash):
            key_store.get_key_entry(fingerprint=fingerprint)
        assert key_store.items() == []

    def test_get_onepass_uid_should_raise_key_error_on_missing_fingerprint(
        self
    ) -> None:
        key_store: AbstractKeyStore = self.key_store_factory()

        with pytest.raises(KeyError, match="not-existing"):
            key_store.get_key_entry(
                fingerprint=KeyFingerprint(
                    length=10, hash="not-existing", comment="x", key_type="some"
                )
            )

    @abc.abstractmethod
    def key_store_factory(self) -> AbstractKeyStore:
        ...


class TestMemoryKeyStore(AbstractKeyStoreTests):
    def key_store_factory(self) -> AbstractKeyStore:
        return MemoryKeyStore()


class TestFileKeyStore(AbstractKeyStoreTests):
    @pytest.fixture(autouse=True)
    def test_dir_factory(self, tmpdir) -> None:
        self.__tmpdir = tmpdir

    def key_store_factory(self) -> AbstractKeyStore:
        return FileKeyStore(file_path=self.__tmpdir / str(uuid.uuid4()))
