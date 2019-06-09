from setuptools import setup

VERSION = "0.0.1"

with open('README.rst', 'r') as f:
    long_description = f.read()
setup(
    name="pyplotsmaps",
    version=VERSION,
    author="dazzHere",
    author_email="dhanushdazz@gmail.com",
    description="A python package for iot projects to plot and locate",
    long_description=long_description,
    url="https://github.com/dazzHere/PY-PLOTS-MAPS",
    packages=['plots_maps'],
    install_requires=['requests'],
    keywords=['iot', 'iot-plots', 'maps', 'maps-iot', 'plots'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "Operating System :: OS Independent",
    ]
)


