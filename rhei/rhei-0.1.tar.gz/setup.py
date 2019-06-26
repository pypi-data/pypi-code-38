import os
from pathlib import Path
from setuptools import setup, Command

from rhei.__version__ import __version__


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')


setup(
    name='rhei',
    version=__version__,
    packages=['rhei'],
    description='Package that implements simple stopwatch class.',
    long_description=Path("README.rst").read_text(),
    author="Damien Krystkiewicz",
    author_email='damian.krystkiewicz@gmail.com',
    keywords=['timer', 'stopwatch'],
    install_requires=[],
    url='https://github.com/dkrystki/rhei',
    python_requires='>=3.7',
    license='Apache 2.0',
    cmdclass={
        'clean': CleanCommand,
    }
)
