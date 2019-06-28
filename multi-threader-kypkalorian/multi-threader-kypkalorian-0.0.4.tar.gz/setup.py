import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="multi-threader-kypkalorian",
    version="0.0.4",
    author="anonymous_donkey_1337",
    author_email="colin.baxter13@gmail.com",
    description="A package for iterating through s3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kypkalorian/multi-threader",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)



