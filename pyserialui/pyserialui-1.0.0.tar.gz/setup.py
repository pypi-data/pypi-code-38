import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyserialui",
    version="1.0.0",
    author="Pat Deegan",
    author_email="pyserialui-contact@devicedruid.com",
    description="SerialUI druid support and examples",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/psychogenic/pyserialui",
    download_url="https://github.com/psychogenic/pyserialui/archive/v1.0.0.tar.gz",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Terminals :: Serial"
    ],
)
