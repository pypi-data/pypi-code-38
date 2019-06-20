import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="html_utils_becothal",
    version="0.4",
    author="Lukas Jedinger",
    author_email="lukas.jedinger@gmail.com",
    description="A tool to inline CSS files into HTML.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/ljedinger/html_utils",
    packages=setuptools.find_packages(),
    classmethod=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved:: MIT License",
        "Operating System:: OS Independent",
    ],
)