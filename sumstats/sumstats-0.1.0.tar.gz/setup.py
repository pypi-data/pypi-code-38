import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='sumstats',
    version='0.1.0',
    author='Anthony Aylward',
    author_email='aaylward@eng.ucsd.edu',
    description='utilities for working with GWAS summary statistics',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/anthony-aylward/sumstats.git',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=['scipy']
)
