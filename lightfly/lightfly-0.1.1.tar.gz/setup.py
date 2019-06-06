import setuptools

with open("DESCRIPTION", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lightfly",
    version="0.1.1",
    author="Weinan Tang",
    author_email="twn39@163.com",
    description="a finance platform for china.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Natural Language :: Chinese (Simplified)",
        "Topic :: Scientific/Engineering :: Mathematics"
    ],
)