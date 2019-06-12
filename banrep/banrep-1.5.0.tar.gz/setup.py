from pathlib import Path
from setuptools import setup, find_packages


here = Path().resolve()

with open("README.md", "r", encoding="utf-8") as fh:
    readme = fh.read()

about = {}
with open(here.joinpath("banrep", "__version__.py"), "r", encoding="utf-8") as f:
    exec(f.read(), about)

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    url=about["__url__"],
    author=about["__author__"],
    author_email=about["__email__"],
    packages=find_packages(exclude=["docs", "tests"]),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Spanish",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
    ],
    python_requires="~=3.7",
    include_package_data=True,
    install_requires=["gensim>=3.4", "pandas>=0.24", "spacy>=2.1", "tika>=1.19"],
)
