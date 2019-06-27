import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="parsini",
    version="0.0.2",
    author="Álvaro García",
    author_email="alvaro.garcia.molino@gmail.com",
    description="Parsea en formato dict y actualiza fichero de configuración",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gmolino/parsini",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
