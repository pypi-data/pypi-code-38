import setuptools

with open("README.md", "r", encoding='UTF-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="afivmax",
    version="0.3.0",
    author="sunao",
    author_email="sunao_0626@hotmail.com",
    description="Interview problem of Ant Fin",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eggachecat/afivmax",
    packages=setuptools.find_packages(exclude=("tests",)),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
)
