import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pitchplots",
    version="1.4.0",
    author="Fabian Moss",
    author_email="fabian.moss@epfl.ch",
    description="A package containing representation tools for musical purposes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DCMLab/pitchplots",
    packages=setuptools.find_packages(),
    package_data={
            'pitchplots': ['data/data_example.mxl'],
    },
    install_requires=['matplotlib>=3.0.1',
                      'pandas>=0.23.4',
                      'numpy>=1.15.3'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)