import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sensor-lib",
    version="0.0.2",
    author="Jason Gao",
    author_email="jgao2299@gmail.com",
    description="Used to collect data taken by Novelda Xethru radar and plot the results",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Justgo13/sensor_lib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)