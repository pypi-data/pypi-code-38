from pathlib import Path

from op_askpass.key_store import MemoryKeyStore, KeyEntry
from op_askpass.operations.list_keys import list_keys


def test_list_keys_should_return_list_of_added_keys(tmp_path: Path) -> None:
    key_store = MemoryKeyStore()
    fingerprint = "some-fingerprint"
    uid = "some-uid"
    path = Path("x")
    key_store.add_fingerprint(fingerprint=fingerprint, onepass_uid=uid, key_path=path)

    keys = list_keys(key_store=key_store)

    assert keys == [(fingerprint, KeyEntry(onepass_uid=uid, key_path=path))]
