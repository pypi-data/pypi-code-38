import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="querytree",
    version="0.1.0",
    author="Quinn Freedman",
    author_email="quinnfreedman@gmail.com",
    description="A data structure for quickly dealing with nested data in different formats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/QuinnFreedman/QueryTree",
    packages=[],  # setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
