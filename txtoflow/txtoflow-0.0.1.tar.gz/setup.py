import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="txtoflow",
    version="0.0.1",
    author="Krishna",
    author_email="krishna.vijay4444@gmail.com",
    description="Library to generate flowcharts from pseudo code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KrishKasula/txtoflow",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
