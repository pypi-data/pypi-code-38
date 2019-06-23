import setuptools

with open("README.md","r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tamarai",
    version="0.0.1",
    author="Roy Attias",
    author_email="roy.attias@outlook.com",
    description="a small package made for learning how to make a package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/boypig24/tamarai",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
