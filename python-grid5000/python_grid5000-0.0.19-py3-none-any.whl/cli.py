import os
import pathlib

from grid5000 import Grid5000

import IPython

CONF_PATH = os.path.join(os.environ.get("HOME"), ".python-grid5000.yaml")

motd=r"""
                 __  __
    ____  __  __/ /_/ /_  ____  ____
   / __ \/ / / / __/ __ \/ __ \/ __ \
  / /_/ / /_/ / /_/ / / / /_/ / / / /
 / .___/\__, /\__/_/ /_/\____/_/ /_/
/_/_________/ _     ___  __________  ____  ____
  / ____/____(_)___/ ( )/ ____/ __ \/ __ \/ __ \
 / / __/ ___/ / __  /|//___ \/ / / / / / / / / /
/ /_/ / /  / / /_/ /  ____/ / /_/ / /_/ / /_/ /
\____/_/  /_/\__,_/  /_____/\____/\____/\____/


* Configuration loaded from %s
* Start exploring the API through the gk variable
  # Example: Get all available sites
  $) gk.sites.list()

""" % CONF_PATH


def main():

    path = pathlib.Path(CONF_PATH)
    if not path.exists():
        print("Configuratio file %s is missing" % CONF_PATH)
        return
    gk = Grid5000.from_yaml(CONF_PATH)

    IPython.embed(header=motd)
