import os
from pathlib import Path

from .env_template import _get_temp_root_env

ENV_FILENAME = ".env.template"
ENV_GLOB = f"*/{ENV_FILENAME}"
PACKAGE_PREFIX = os.environ["CS_PACKAGE_PREFIX"]
PROJECT_LIBS_PATH = Path(os.environ["CS_PROJECT_LIBS_PATH"])


def concat_dotenv_templates(pipenv, libs_path=PROJECT_LIBS_PATH):
    """Return an iterable of deduped lines from all concatenated env files."""
    root_env_path = _get_temp_root_env()
    libs_path = Path(pipenv.root_path, libs_path)
    core_env_path = Path(libs_path, f"{PACKAGE_PREFIX}core", ENV_FILENAME)
    lib_env_paths = [p for p in libs_path.glob(ENV_GLOB) if p != core_env_path]
    return DotEnvCat(root_env_path, core_env_path, *sorted(lib_env_paths))


class DotEnvCat:
    """Concatenate, deduplicate, and format .env files into one."""

    def __init__(self, *paths):
        """Initialize the DotEnvCat instance."""
        self.paths = list(paths)

    def __iter__(self):
        """Parse and return the lines from every included env file."""
        paths_seen = set()
        keys_seen = set()
        for path in self.paths:
            if path not in paths_seen and path.exists():
                paths_seen.add(path)
                with path.open() as f:
                    yield from self._parse_env(f, keys_seen)
    
    def _parse_env(self, dotenv, keys_seen):
        """Yield after deduplicating, formatting, and stripping whitespace."""
        prev_line_blank = True
        for line in dotenv:
            line = line.strip()
            if line:
                prev_line_blank = False
                if "=" not in line:
                    yield line + "\n"
                else:
                    key, val = line.split("=", maxsplit=1)
                    key, val = key.strip(), val.strip()
                    if key not in keys_seen:
                        keys_seen.add(key)
                        yield f"{key}={val}\n"
            elif not prev_line_blank:
                prev_line_blank = True
                yield "\n"
 
