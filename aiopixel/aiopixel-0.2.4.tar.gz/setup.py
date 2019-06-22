from distutils.core import setup
from setuptools import find_packages


def get_requirements():
    with open("requirements.txt") as f:
        requirements = f.read().splitlines()
    return requirements


setup(
    name="aiopixel",
    version="0.2.4",
    packages=find_packages(include=["aiopixel", "aiopixel.*"]),
    license="GPLv3",
    install_requires=get_requirements(),
    python_requires=">=3.5",
    url="https://github.com/palmtree5/aiopixel",
    author="palmtree5",
    author_email="",
)
