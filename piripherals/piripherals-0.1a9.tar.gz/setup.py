from os.path import join, dirname
from setuptools import setup  # , find_packages


def read(f): return open(join(dirname(__file__), f)).read()


exec(read('piripherals/__version__.py'))


setup(
    name=__title__,
    version=__version__,
    license=__license__,
    description=__description__,
    author=__author__,
    author_email=__author_email__,
    url=__url__,
    packages=['piripherals'],  # find_packages(),
    python_requires='>=3.5',
    # install_requires=['rpi_ws281x'],
    # setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    extras_require={
        'LED': ["rpi_ws281x"],
        'GPIO': ['RPi.GPIO'],
        'I2C': ['smbus2'],
        'MPD': ['python-mpd2']
    },
    aliases={'test': 'pytest'},
    entry_points={
        'console_scripts': [
            'mpr121-dump = piripherals.mpr121:main',
            'led-test = piripherals.led:main [LED]',
        ]
    },
)
