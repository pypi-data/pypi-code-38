import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lipo2pol-fdas",
    version="0.0.2",
    author="Fevzi Das",
    author_email="fevzidas@gmail.com",
    description="Converts LineString and Point data in Geojson format to Polygon data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)