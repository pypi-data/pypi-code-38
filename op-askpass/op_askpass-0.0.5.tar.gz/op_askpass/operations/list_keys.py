from typing import List, Tuple

from op_askpass.key_store import AbstractKeyStore


def list_keys(key_store: AbstractKeyStore) -> List[Tuple[str, str]]:
    return key_store.items()
