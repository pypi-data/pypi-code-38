"""
setup module
"""
from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="Kawhi",
    version="0.0.45",
    description="A package inspired by Kawhi Leonard of the Toronto Raptors",
    py_modules=["kawhi.kawhi", "kawhi.get_jokes"],
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests"],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
