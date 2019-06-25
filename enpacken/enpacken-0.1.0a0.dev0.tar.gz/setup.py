"""Install *enpacken*.

Usage: pip install .
"""

import pathlib
import setuptools

parent = pathlib.Path(__file__).parent
long_description = (parent / "README.md").read_text()
version = (parent / "VERSION").read_text().strip()
classifiers = [
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3 :: Only",
    "Natural Language :: English",
    "Operating System :: POSIX :: Linux",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: MacOS",
    "License :: OSI Approved :: MIT License"]

setuptools.setup(
    name="enpacken",
    version=version,
    description="Find package installation candidates",
    author="Laurie",
    author_email="laurie_opperman@hotmail.com",
    maintainer="Laurie",
    maintainer_email="laurie_opperman@hotmail.com",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=classifiers,
    keywords="package wheel distribution platform candidate",
    project_urls={
        "Source": "https://github.com/EpicWink/enpacken",
        "Bugs": "https://github.com/EpicWink/enpacken/issues"},
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    extras_require={"dev": ["pytest", "pytest-cov"]},
    entry_points={"console_scripts": ["enpacken=enpacken.__main__:main"]}
)
