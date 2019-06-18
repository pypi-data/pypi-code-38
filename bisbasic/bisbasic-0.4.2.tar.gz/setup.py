import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bisbasic",
    version="0.4.2",
    author="Bismuth Foundation",
    author_email="admin@bismuth.cz",
    description="Bismuth Blockchain Dependencies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bismuthfoundation/Bismuth",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)