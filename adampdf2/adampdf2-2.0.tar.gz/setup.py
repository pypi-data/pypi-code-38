import setuptools
from pathlib import Path
setuptools.setup(
    name="adampdf2",
    version=2.0,
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages()
)
