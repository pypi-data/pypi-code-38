import setuptools

setuptools.setup(
    name="pypi_example",
    version="0.0.1",
    author="Berlin Hsin",
    author_email="berlin.hsin@gmail.com",
    description="A small example package",
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
