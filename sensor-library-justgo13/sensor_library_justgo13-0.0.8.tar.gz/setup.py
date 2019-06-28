import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sensor_library_justgo13",
    version="0.0.8",
    author="Jason Gao",
    author_email="jgao2299@gmail.com",
    description="Library for radar parser code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Justgo13/sensor_library",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
