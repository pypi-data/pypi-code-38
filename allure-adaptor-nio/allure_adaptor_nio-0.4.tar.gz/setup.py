import os
import sys
from setuptools import setup

PACKAGE = "allure_adaptor_nio"
VERSION = "0.4"

install_requires = [
    "lxml>=3.2.0",
    "pytest>=2.7.3",
    "namedlist",
    "six>=1.9.0"
]

if sys.version_info < (3, 4):
    install_requires.append("enum34")


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def main():
    setup(
        name=PACKAGE,
        version=VERSION,
        description=("change get_marker to get_closest_marker"),
        author="",
        packages=["allure"],
        entry_points={'pytest11': ['allure_adaptor = allure.pytest_plugin']},
        install_requires=install_requires
    )


if __name__ == '__main__':
    main()
