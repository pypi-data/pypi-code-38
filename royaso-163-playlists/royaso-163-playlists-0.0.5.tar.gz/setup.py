import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="royaso-163-playlists",
    version="0.0.5",
    author="royaso",
    author_email="zhangroyaso@gmail.com",
    description="royaso  package for 163 music ranking download playlists",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/royaso/ok",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
