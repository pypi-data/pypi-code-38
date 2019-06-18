import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xorCryptPy",
    version="1.0.1",
    author="Ivo Ilić",
    author_email="admin@ivoilic.com",
    description="Simple Python XOR string encryption library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ivoilic/XOR-Crypt-Python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
