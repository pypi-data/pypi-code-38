from setuptools import setup , find_packages

with open("README.md","r") as fh:
	long_description = fh.read()

setup(
    name = "malogin",
    version = "0.1.2",
    author = "bluesky8",
    author_email = "guohaiyin8@gmail.com",
    url = "https://github.com/yinguohai",
    description = u'get cookies of malogin',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    packages = find_packages(),
    install_requires= [],
    classifiers = [
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
