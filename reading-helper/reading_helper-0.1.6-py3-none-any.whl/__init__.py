import toml
from pathlib import Path

pyproject = toml.load(str(Path(__file__).parents[1] / "pyproject.toml"))
__version__ = pyproject["tool"]["poetry"]["version"]
del pyproject
