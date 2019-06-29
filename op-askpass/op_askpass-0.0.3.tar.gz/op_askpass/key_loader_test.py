import abc
from pathlib import Path

from op_askpass.key_loader import AbstractKeyLoader, MemoryKeyLoader


class AbstractKeyLoaderTests(abc.ABC):
    @abc.abstractmethod
    def key_loader_factory(self) -> AbstractKeyLoader:
        ...

    def test_list_loaded_keys_should_return_empty_list_when_empty(self) -> None:
        loader = self.key_loader_factory()

        actual = loader.list_loaded_keys()

        assert actual == []

    def test_load_key_should_correctly_load_given_key(self) -> None:
        loader = self.key_loader_factory()
        fingerprint_generator = loader.get_fingerprint_generator()
        key_path = Path(__file__).parent / "test_data" / "test_key"

        loader.load_key(
            key_path=key_path,
            op_domain="some-domain",
            op_uid="some-uid",
            op_session_key="some-key",
        )

        assert loader.list_loaded_keys() == [fingerprint_generator.for_path(key_path)]


class TestMemoryKeyLoader(AbstractKeyLoaderTests):
    def key_loader_factory(self) -> AbstractKeyLoader:
        return MemoryKeyLoader()
