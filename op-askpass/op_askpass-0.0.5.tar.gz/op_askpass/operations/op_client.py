import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from op_askpass.key_loader import AbstractKeyLoader
from op_askpass.key_store import AbstractKeyStore

__all__ = ["get_password_from_op", "login_to_op", "setup_op_client"]


def __download_op_client(download_url: str, download_dir: Path) -> None:
    subprocess.check_call(["wget", download_url], cwd=str(download_dir))


def __unzip_op_client_archive(archive_path: Path, extract_dir: Path) -> None:
    subprocess.check_call(["unzip", str(archive_path)], cwd=str(extract_dir))


def __verify_signature(client_path: Path, signature_file: Path) -> None:
    subprocess.check_call(["gpg", "--verify", str(signature_file), str(client_path)])
    return


def __signin_to_op(executable: Path, domain: str, email: str) -> None:
    subprocess.check_call([str(executable), "signin", domain, email, "--output=raw"])


def get_password_from_op(executable: Path, item_name: str) -> str:
    output = (
        subprocess.check_output([str(executable), "get", "item", item_name])
        .decode("utf-8")
        .strip()
    )
    obj = json.loads(output)
    return obj["details"]["password"]


def login_to_op(
    executable: Path,
    op_domain: str,
    key_store: AbstractKeyStore,
    key_loader: AbstractKeyLoader,
) -> None:
    session_key = (
        subprocess.check_output([str(executable), "signin", op_domain, "--output=raw"])
        .decode("utf-8")
        .strip()
    )
    loaded_fingerprints = set(key_loader.list_loaded_keys())
    for fingerprint, key_entry in key_store.items():
        if fingerprint in loaded_fingerprints:
            print(f"Skipping key {key_entry.key_path}. Already loaded.")
            continue

        key_loader.load_key(
            key_path=key_entry.key_path,
            op_domain=op_domain,
            op_session_key=session_key,
            op_uid=key_entry.onepass_uid,
        )


def setup_op_client(
    download_url: str,
    install_path: Path,
    op_domain: str,
    op_email: str,
    verify: bool = True,
) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(str(tmpdir))
        download_dir = tmpdir / "downloaded_client"
        download_dir.mkdir()
        __download_op_client(download_url=download_url, download_dir=download_dir)

        extract_dir = tmpdir / "extracted_client"
        extract_dir.mkdir()
        __unzip_op_client_archive(
            archive_path=download_dir / "op_linux_amd64_v0.5.7.zip",
            extract_dir=extract_dir,
        )

        if verify:
            __verify_signature(
                client_path=extract_dir / "op", signature_file=extract_dir / "op.sig"
            )

        shutil.copy(src=str(extract_dir / "op"), dst=str(install_path / "op"))

    __signin_to_op(executable=install_path / "op", domain=op_domain, email=op_email)
