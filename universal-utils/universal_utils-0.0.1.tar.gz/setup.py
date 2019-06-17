import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="universal_utils",
    version="0.0.1",
    author="tsotsi",
    author_email="tsotsi@tsotsi.cn",
    description="python utils",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Tsotsi/python_utils",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
