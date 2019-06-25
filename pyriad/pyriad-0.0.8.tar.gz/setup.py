import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyriad",
    version="0.0.8",
    author="Teodor Scorpan",
    author_email="teodor.scorpan@gmail.com",
    description="Clustering with natural algorithms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PyNature/pyriad",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
