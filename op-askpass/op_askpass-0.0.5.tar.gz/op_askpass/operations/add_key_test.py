from pathlib import Path

from op_askpass.fingerprint_generator import MD5FingerprintGenerator
from op_askpass.key_store import MemoryKeyStore, KeyEntry
from op_askpass.operations.add_key import add_key_from_path


def test_add_key_should_add_key_from_path(tmp_path: Path) -> None:
    key_path = tmp_path / "yada.txt"
    key_path.write_text("xxx")
    key_store = MemoryKeyStore()
    fingerprint_generator = MD5FingerprintGenerator()
    uid = "some-uid"

    add_key_from_path(
        path=key_path,
        onepass_uid=uid,
        fingerprint_generator=fingerprint_generator,
        key_store=key_store,
    )

    assert key_store.get_key_entry(
        fingerprint=fingerprint_generator.for_path(key_path)
    ) == KeyEntry(onepass_uid=uid, key_path=key_path)
