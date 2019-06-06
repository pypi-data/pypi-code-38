import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="feuersoftware",
    version="0.1.0",
    author="Bouni",
    author_email="bouni@owee.de",
    description="A Feuersoftware public API implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bouni/feuersoftware",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
