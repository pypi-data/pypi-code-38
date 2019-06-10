import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="inapp_file_util-rjanoop",
    version="1.0.0",
    author="RJ Anoop",
    author_email="mail.anooprj@gmail.com",
    description="Utility to read and write raw data file and other utility functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rjanoop/inapp_file_util",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)