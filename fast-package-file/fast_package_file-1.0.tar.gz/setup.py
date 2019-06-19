import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fast_package_file",
    version="1.0",
    author="Kataiser",
    author_email="mecharon1.gm@gmail.com",
    description="Package a directory to a file, with fast file access and compression support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Kataiser/fast-package-file",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)