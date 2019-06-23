import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="udacity-CarNDT1Test",
    version="1.1.0",
    description="Tutorial for creating a pypi package",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/feng3245/ourtest",
    author="SDCT1",
    author_email="testSDCT1@udacity.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
	"Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["ourtest"],
    include_package_data=True,
    install_requires=["matplotlib"],
)
