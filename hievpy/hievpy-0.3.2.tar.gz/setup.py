import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hievpy",
    version="0.3.2",
    author="Gerard Devine, Dan Metzen",
    author_email="gerarddevine@gmail.com",
    description="Python 3 wrapper for the HIEv Data Capture Application API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gdevine/hievpy",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
      'pandas',
      'tqdm',
      'requests',
      'certifi',
    ],
)

