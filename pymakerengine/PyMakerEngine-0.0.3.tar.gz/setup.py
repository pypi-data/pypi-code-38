import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyMakerEngine",
    version="0.0.3",
    author="iByNiki_",
    author_email="therealpingmc@gmail.com",
    description="Make games with python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://discord.gg/9nTu3kW",
    packages=setuptools.find_packages(),
    keywords=["games", "python games", "game", "pygame"],
    install_requires=[
        "keyboard==0.13.3"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
