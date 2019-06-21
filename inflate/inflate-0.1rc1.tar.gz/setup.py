# -*- coding: utf-8 -*-

import re
from setuptools import setup


version = re.search(
    '^__version__\s*=\s*"(.*)"', open("inflate/inflate.py").read(), re.M
).group(1)


with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(
    name="inflate",
    packages=["inflate"],
    package_data={"inflate": ["data/*.json"]},
    entry_points={"console_scripts": ["inflate = inflate.inflate:main"]},
    version=version,
    description="inflate lets you compute how much money is worth in different years",
    long_description=long_descr,
    long_description_content_type="text/markdown",
    author="Zain Patel",
    author_email="zain.patel06@gmail.com",
    url="https://github.com/mzjp2/inflation",
    classifiers=[
        # Pick your license as you wish
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="money command line interface inflation cli",
    python_requires=">=3.5",
    install_requires=["click", "colorama"],
)

