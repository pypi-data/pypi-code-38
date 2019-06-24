import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="secrypt",
    version="1.0.1",
    author="Rubbie Kelvin",
    author_email="rubbiekelvinvoltsman@gmail.com",
    description="Crypting library for python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rubbieKelvin/secrypt",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)