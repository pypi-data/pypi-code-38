import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyquake",
    version="1.0.0",
    author="Cooper Barth",
    author_email="cooperfbarth@gmail.com",
    description="A package enabling the synthesis of seismic audio.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cooperbarth/PyQuake",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)