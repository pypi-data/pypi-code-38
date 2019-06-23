import setuptools
from m2c.version import version

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="m2c",
    version=version,
    author="yangbinnnn",
    author_email="yangbinnnn@gmail.com",
    description="m2c",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yangbinnnn/m2c",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pyyaml",
        "psutil",
        "watchdog"
    ],
    scripts=['bin/m2c'],
)
