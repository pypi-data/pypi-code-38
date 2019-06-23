from setuptools import  setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="lipo2pol",
    version="0.0.2.2",
    author="Fevzi Das",
    author_email="fevzidas@gmail.com",
    description="Converts LineString and Point data format to Polygon data in Geojson",
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=['lipo2pol'],
    package_dir={'': 'lipo2pol'},
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)