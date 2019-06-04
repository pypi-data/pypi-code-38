import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Vectorial",
    version="0.0.1",
    author="Jônathas Gouveia",
    author_email="jonathas_gouv@hotmail.com",
    description="A vector module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jonathasgouv/pyvector",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)