import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="binarypipe",
    version="0.0.1",
    author="Shivam Agrawal",
    author_email="shivam301296@gmail.com",
    description="Import binary data such as images, audio in ready to feed format for ML models with just one line of code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shivampip/BinaryPipe",
    packages=setuptools.find_packages(),
    install_requires=['numpy', 'matplotlib', 'tensorflow'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)