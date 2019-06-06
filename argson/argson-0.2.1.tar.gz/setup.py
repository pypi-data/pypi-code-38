import setuptools

from argson import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="argson",
    version=__version__,
    author="Gabriel Chamon",
    author_email="gchamon@live.com",
    description="Manage arguments from a JSON file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gchamon/argson",
    packages=setuptools.find_packages(),
    platforms='any',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>3.6'
)
