import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lipo2pol",
    version="0.0.2.1",
    author="Fevzi Das",
    author_email="fevzidas@gmail.com",
    description="Converts LineString and Point data format to Polygon data in Geojson",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    include_package=True,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)