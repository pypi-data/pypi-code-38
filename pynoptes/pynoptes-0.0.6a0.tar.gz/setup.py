import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pynoptes",
    version="0.0.6a",
    author="Fabian Herzog",
    author_email="mail@fabianherzog.me",
    description="Python Package for Object Detection and Tracking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fubel/pynoptes",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)