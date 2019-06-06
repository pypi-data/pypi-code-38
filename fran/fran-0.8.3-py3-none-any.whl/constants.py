from pathlib import Path

import toml

here = Path(__file__).absolute()
package_dir = here.parent
config_path = package_dir / "config.toml"

default_config = toml.load(config_path)

DEFAULT_CACHE_SIZE = default_config["settings"]["cache"]
DEFAULT_FPS = default_config["settings"]["fps"]
DEFAULT_THREADS = default_config["settings"]["threads"]
DEFAULT_FLIPX = default_config["transform"]["flipx"]
DEFAULT_FLIPY = default_config["transform"]["flipy"]
DEFAULT_ROTATE = default_config["transform"]["rotate"]
DEFAULT_KEYS = default_config["keys"]

controls_path: Path = package_dir / "controls.txt"

CONTROLS = controls_path.read_text().strip()

# framewise log level
FRAME_LEVEL = 5
