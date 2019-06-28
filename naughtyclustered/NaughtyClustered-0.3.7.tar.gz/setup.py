from setuptools import setup
__project__ = "NaughtyClustered"
__version__ = "0.3.7"
__description__ = "Clustered version of Naughty and Nice with a few more addons"
__packages__ = ["NaughtyClustered"]
__author__ = "xXTheProgrammerXx"
__author_email__ = "arhithprem@gmail.com"
__classifiers__ = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Education",
    "Programming Language :: Python :: 3"
]
__keywords__ = ["classifing", "learning"]
with open("README.md", "r", encoding="utf-8") as f:
    __long_description__ = f.read()
__requires__ = ["tweepy", "nltk", "dispy"]
setup(
    long_description_content_type = "text/markdown",
    name = __project__,
    version = __version__,
    description = __description__,
    packages = __packages__,
    author = __author__,
    author_email = __author_email__,
    classifiers = __classifiers__,
    keywords = __keywords__,
    long_description = __long_description__,
    requires = __requires__
)
