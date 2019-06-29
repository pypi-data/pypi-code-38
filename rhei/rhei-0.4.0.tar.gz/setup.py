#  type: ignore
from typing import List

import os

from setuptools import setup, Command


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options: List = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')


setup(
    setup_requires=['pbr'],
    pbr=True,
    cmdclass={
        'clean': CleanCommand,
    }
)
