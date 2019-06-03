import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CLI-csdummi",
    version="1.0.0",
    author="Joris Gutjahr",
    author_email="joris.gutjahr@gmail.com",
    description="A framework to write CLI projects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/csdummi/cli_framework",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ]
)
