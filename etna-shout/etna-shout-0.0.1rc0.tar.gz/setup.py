import os

from setuptools import setup


HERE = os.path.dirname(os.path.realpath(__file__))
requirements = HERE + '/requirements.txt'
deps = []
if os.path.isfile(requirements):
    with open(requirements) as f:
        deps = f.read().splitlines()

setup(
    name="etna-shout",
    version="0.0.1-rc",
    description="Command line tool to interact with ETNA's APIs",
    url="https://github.com/tbobm/shout",
    author='Theo "Bob" Massard',
    author_email="massar_t@etna-alternance.net",
    license="Apache License 2.0",
    packages=['shout'],
    install_requires=deps,
    entry_points={"console_scripts": ["shout=shout:main"]},
)
