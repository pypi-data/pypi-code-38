import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tiquations",
    version="1.2",
    author="Tinos Psomadakis",
    author_email="tinosps@gmail.com",
    description="Tiquations is an Open-Source Python package that is aimed at giving mathematicians and scientists easy access to important equations that they may use often. It was made in python 3.7 and should work on all versions higher than 3.0.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://tiquations.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
            ],
)
