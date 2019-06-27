import os
from pathlib import Path
par_dir = Path(__file__).parent

with open(os.path.join(par_dir,  "VERSION"), "r") as vfh:
    __version__ = vfh.read()