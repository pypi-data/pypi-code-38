import pathlib
from setuptools import setup

CURRENT_DIR = pathlib.Path(__file__).parent
README = (CURRENT_DIR / "README.md").read_text()

setup(
    name="threadsafe",
    version="1.0.0",
    description="Thread-safe data structures",
    long_description=README,
    long_description_type="text/markdown",
    url="https://github.com/KingAkeem/threadsafe",
    author="Akeem King",
    author_email="akeemtlking@gmail.com",
    license="GNU GPLv3",
    packages=["threadsafe"],
    include_package_data=True
)


