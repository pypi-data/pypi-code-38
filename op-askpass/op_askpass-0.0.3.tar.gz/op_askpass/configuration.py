from pathlib import Path


def get_configuration_directory() -> Path:
    dir = Path.home() / ".op-askpass"
    dir.mkdir(exist_ok=True)
    return dir
