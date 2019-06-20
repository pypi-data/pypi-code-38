import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="BlastML",
    version="0.2.7",
    author="Shany Golan",
    author_email="shanytc@gmail.com",
    description="BlastML is a Fast Machine Learning Prototyping Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shanytc/BlastML",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
