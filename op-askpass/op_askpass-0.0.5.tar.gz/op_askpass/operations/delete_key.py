from pathlib import Path

from op_askpass.fingerprint_generator import AbstractFingerprintGenerator
from op_askpass.key_store import AbstractKeyStore


def delete_key_from_path(
    path: Path,
    fingerprint_generator: AbstractFingerprintGenerator,
    key_store: AbstractKeyStore,
) -> None:
    fingerprint = fingerprint_generator.for_path(path=path)
    key_store.delete_fingerprint(fingerprint=fingerprint)
