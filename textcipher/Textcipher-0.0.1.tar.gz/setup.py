import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Textcipher",
    version="0.0.1",
    author="Ashish Shetty",
    author_email="shetty073@gmail.com",
    description="A text encryption/decryption package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Shetty073/Textcipher",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
