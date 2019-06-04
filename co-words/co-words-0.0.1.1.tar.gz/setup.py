import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="co-words",
    version="0.0.1.1",
    author="Kasey Jones",
    author_email="krjones@rti.org",
    description="A python package to complete co-occurring word counts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RTIInternational/co-words",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
