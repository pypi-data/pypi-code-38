from setuptools import setup
__project__ = "All you need module"
__version__ = "0.0.1"
__description__ = "A python module with all you need"
__packages__ = ["AYNM"]
__author__ = "khhs"
__author_email__ = "khhs1671@gmail.com"
__classifiers__ = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Education",
    "Programming Language :: Python :: 3",
]
__requires__ = ["webbrowser", "tkinter"]

setup(
    name = __project__,
    version = __version__,
    description = __description__,
    packages = __packages__,
    author = __author__,
    author_email = __author_email__,
    classifiers = __classifiers__,
    requires = __requires__
)
