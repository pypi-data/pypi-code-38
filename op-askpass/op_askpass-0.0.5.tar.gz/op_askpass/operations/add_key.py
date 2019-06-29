from pathlib import Path

from op_askpass.fingerprint_generator import AbstractFingerprintGenerator
from op_askpass.key_store import AbstractKeyStore


def add_key_from_path(
    path: Path,
    onepass_uid: str,
    fingerprint_generator: AbstractFingerprintGenerator,
    key_store: AbstractKeyStore,
) -> None:
    fingerprint = fingerprint_generator.for_path(path=path)
    key_store.add_fingerprint(
        fingerprint=fingerprint, onepass_uid=onepass_uid, key_path=path.absolute()
    )
