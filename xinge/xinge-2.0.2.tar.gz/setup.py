import ast
import re
import setuptools

_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("xinge_push/__init__.py") as f:
    VERSION = ast.literal_eval(_version_re.search(f.read()).group(1))

NAME = "xinge"

DESCRIPTION = "xinge Push API for Python(http://xg.qq.com)."
LONG_DESCRIPTION = open("README.rst").read()

KEYWORDS = ["xinge", "Android Push", "iOS Push", "push"]

AUTHOR = "observer"
AUTHOR_EMAIL = "764664@gmail.com"
LICENSE = "MIT"

URL = "https://github.com/jie17/xinge-api-python"

setuptools.setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    platforms="any",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
    keywords=KEYWORDS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=["requests"],
)
