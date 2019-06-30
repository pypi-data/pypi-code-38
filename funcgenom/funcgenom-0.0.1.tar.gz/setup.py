import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='funcgenom',
    version='0.0.1',
    author='Anthony Aylward',
    author_email='aaylward@eng.ucsd.edu',
    description='Classes and functions for functional genomics analysis',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/anthony-aylward/funcgenom.git',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=['coloc', 'py1kgp', 'pyhg19', 'sumstats']
)
