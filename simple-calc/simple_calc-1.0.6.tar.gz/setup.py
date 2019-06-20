import pathlib
from setuptools import setup, find_packages

# The directory containing the file
HERE = pathlib.Path(__file__).parent

# The Text of the README File
README = (HERE / "README.md").read_text()

setup(
    name="simple_calc",
    version="1.0.6",
    description="A simple GUI Calculator for normal, basic operations",
    long_description=README,
    long_description_content_type="text/markdown",
    url="",
    author="",
    author_email="",
    license="MIT",
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "calc=simple_calc.__main__:main",
        ]
    },

)