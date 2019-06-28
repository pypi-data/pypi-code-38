import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="decon",
    version="0.0.1",
    author="Michael Haas",
    author_email="micha2718l@gmail.com",
    description="Deconvolution tools, focused on time series data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/micha2718l/decon",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)