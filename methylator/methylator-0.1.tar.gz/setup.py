from setuptools import setup, find_packages

setup(
    name="methylator",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "methylator = methylator.splitReads:topLevel"
        ]
    }
)
