
import setuptools

with open("README.md", "r") as f:
    long_description = f.read()
    f.close()

setuptools.setup(
    name="idebug",
    version="0.0.17",
    author="innovata sambong",
    author_email="iinnovata@gmail.com",
    description="innovata-debug",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/innovata/idebug",
    packages=setuptools.find_packages(exclude=["*.jupyter", "*.jupyter.*", "jupyter.*", "jupyter"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
