import setuptools
from asserty import version, name

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=name,
    version=version,
    author="Jonathan Lundholm",
    author_email="jon.lundholm@gmail.com",
    description="A utility package for making better test assertions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lunjon/asserty",
    packages=[name],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)