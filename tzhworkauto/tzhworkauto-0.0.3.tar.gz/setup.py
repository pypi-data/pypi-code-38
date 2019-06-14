import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tzhworkauto",
    version="0.0.3",
    author="tzh",
    author_email="13060820957@163.com",
    description="A package for auto work of oa sheet ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/664956016/tzhworkauto.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
