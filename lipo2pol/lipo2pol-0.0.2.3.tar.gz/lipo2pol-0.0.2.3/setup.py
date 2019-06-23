from setuptools import setup

long_description = 'This tool converts LineString and Point data in Geojson format to Polygon data.  \
                   The package obtains information such as number of lanes,  width of lanes from OSM data. '

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="lipo2pol",
    version="0.0.2.3",
    author="Fevzi Das",
    author_email="fevzidas@gmail.com",
    description="Converts LineString and Point data format to Polygon data in Geojson",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)