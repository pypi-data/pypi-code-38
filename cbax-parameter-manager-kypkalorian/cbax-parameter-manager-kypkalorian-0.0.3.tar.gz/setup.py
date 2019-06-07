import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cbax-parameter-manager-kypkalorian",
    version="0.0.3",
    author="anonymous_donkey_1337",
    author_email="colin.baxter13@gmail.com",
    description="A small example/test package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kypkalorian/cbax_parameter_manager",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

