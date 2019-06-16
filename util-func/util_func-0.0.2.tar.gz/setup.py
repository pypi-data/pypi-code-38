import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="util_func",
    version="0.0.2",
    author="Rong hsu",
    author_email="s5952360@gmail.com",
    description="Python utility function library.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TaiRongSyuStudio/util_func.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
