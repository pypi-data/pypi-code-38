from setuptools.command.install import install
from setuptools import setup, find_packages
from os.path import abspath, dirname, join
import sys, os, stat, json
from pathlib import Path
import mmap

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 6)

# This check and everything above must remain compatible with Python 2.7.
if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write("""
==========================
Unsupported Python version
==========================
This version of Lumavate CLI requires Python {}.{}, but you're trying to
install it on Python {}.{}.
This may be because you are using a version of pip that doesn't
understand the python_requires classifier. Make sure you
are installing with pip3, then try again:
    $ pip3 install .
""".format(*(REQUIRED_PYTHON + CURRENT_PYTHON)))
    sys.exit(1)

cli_path = str(Path.home()) + '/.luma_cli_config'
cli_cache = str(Path.home()) + '/.luma_cache'

if not os.path.exists(cli_path):
    with open(cli_path, 'w+') as config:
        json.dump({ "envs": {}, "profiles": {} }, config)

# Don't worry about overwriting cache
with open(cli_cache, 'w+') as config:
    json.dump({ "user": {} }, config)

os.chmod(cli_path, 0o666)
os.chmod(cli_cache, 0o666)

# Read the version number from version.py
with open(abspath(join(dirname(__file__), 'cli', 'version.py'))) as versionFile:
	__version__ = versionFile.read().strip().replace('__version__ = ', '').replace("'", '')

with open('README.md') as f:
    long_description = f.read()

setup(
    name="luma",
    version=__version__,
    description='A CLI to interact with the Lumavate platform',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Gunnar Norred',
    author_email='g.norred@lumavate.com',
    python_requires='>={}.{}'.format(*REQUIRED_PYTHON),
    data_files=[('lumavate-cli', ['cli/images/default-icon.svg'])],
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    install_requires=[
        'click>=7.0',
        'pycparser==2.18',
        'pyparsing==2.2.0',
        'python-dateutil==2.7.3',
        'requests==2.19.1',
        'docker==4.0.1',
        'PyQRCode==1.2.1'
    ],
    entry_points='''
        [console_scripts]
        luma=cli.cli:cli
    '''
)

zshrc = str(Path.home()) + '/.zshrc'
bashrc = str(Path.home()) + '/.bash_profile'

tab_comp = False

if os.path.exists(zshrc):
    with open(zshrc, 'rb', 0) as zsh_config, mmap.mmap(zsh_config.fileno(), 0, access=mmap.ACCESS_READ) as s:
        if s.find(b'_LUMA_COMPLETE=source_zsh luma') != -1:
            tab_comp = True
            print("Completion already activated for ZSH")

    if tab_comp is False:
        with open(zshrc, 'a') as zsh:
            zsh.write('eval "$(_LUMA_COMPLETE=source_zsh luma)"')

if os.path.exists(bashrc):
    with open(bashrc, 'rb', 0) as bash_config, mmap.mmap(bash_config.fileno(), 0, access=mmap.ACCESS_READ) as s:
        if s.find(b'_LUMA_COMPLETE=source luma') != -1:
            tab_comp = True
            print("Completion already activated for Bash")

    if tab_comp is False:
        with open(bashrc, 'a+') as bash:
            bash.write('eval "$(_LUMA_COMPLETE=source luma)"')
else:
    with open(bashrc, 'a+') as bash:
        bash.write('eval "$(_LUMA_COMPLETE=source luma)"')
