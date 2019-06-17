from setuptools import setup
__project__ = "SwanOS"
__version__ = "0.0.3"
__description__ = "A Very Simple Python OS"
__packages__ = ["os"]
__classifiers__ = [
    "Programming Language :: Python :: 3",
]
__author_email__ = 'forsbergw82@gmail.com'
setup(
    name = __project__,
    version = __version__,
    description = __description__,
    packages = __packages__,
    classifiers = __classifiers__,
    author_email = __author_email__,
)