from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = fh.read().splitlines()

with open("dev_requirements.txt", "r") as fh:
    dev_requirements = fh.read().splitlines()

setup(
    name="op_askpass",
    version="0.0.3",
    author="Maciej Gol",
    author_email="1kroolik1@gmail.com",
    description="Add password-protected ssh keys promptless using 1Password.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=["op_askpass"],
    install_requires=requirements,
    extras_require={"dev": dev_requirements},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Unix",
        "Environment :: Console",
        "Typing :: Typed",
    ],
    entry_points={
        "console_scripts": [
            "op-askpass=op_askpass.cli.main:main",
            "op-askpass-get-password=op_askpass.cli.get_password:main",
        ]
    },
)
