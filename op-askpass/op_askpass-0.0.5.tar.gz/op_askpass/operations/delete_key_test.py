from pathlib import Path

from op_askpass.fingerprint_generator import MD5FingerprintGenerator
from op_askpass.key_store import MemoryKeyStore
from op_askpass.operations.delete_key import delete_key_from_path


def test_delete_key_from_path_should_remove_the_key(tmp_path: Path) -> None:
    key_path = tmp_path / "yada.txt"
    key_path.write_text("xxx")
    key_store = MemoryKeyStore()
    fingerprint_generator = MD5FingerprintGenerator()
    uid = "some-uid"
    fingerprint = fingerprint_generator.for_path(key_path)
    key_store.add_fingerprint(
        fingerprint=fingerprint, onepass_uid=uid, key_path=key_path
    )

    delete_key_from_path(
        path=key_path, fingerprint_generator=fingerprint_generator, key_store=key_store
    )

    assert key_store.items() == []
