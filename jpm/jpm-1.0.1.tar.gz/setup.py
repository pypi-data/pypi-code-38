import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jpm",
    version="1.0.1",
    author="Brandon Benefield",
    author_email="bsquared18@gmail.com",
    description="A small CLI package manager for Java projects using Maven",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bbenefield89/Java_Package_Manager",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    scripts=[
        'bin/jpm'
    ],
)