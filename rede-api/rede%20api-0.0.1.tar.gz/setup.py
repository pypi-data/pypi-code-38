import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rede api",
    version="0.0.1",
    author="Darlei Soares",
    author_email="darleisantossoares@gmail.com",
    license="MIT",
    description="A package to handle rede API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/darleisantossoares/rede_api",
    packages=setuptools.find_packages(),
    install_requires=["requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)