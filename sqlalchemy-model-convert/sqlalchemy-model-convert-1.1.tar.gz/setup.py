import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
    print(long_description)

setuptools.setup(
    name="sqlalchemy-model-convert",
    version="1.1",
    author="tystudy",
    author_email="",
    description="Use simple and convenient model transform dictionary module(Python3)",
    long_description="Use simple and convenient model transform dictionary module(Python3)",
    long_description_content_type="text/markdown",
    url="https://github.com/persistty/sqlalchemy-model-convert",
    packages=setuptools.find_packages()
)
