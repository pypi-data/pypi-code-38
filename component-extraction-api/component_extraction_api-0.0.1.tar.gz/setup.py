import setuptools

with open("README", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="component_extraction_api",
    version="0.0.1",
    author="Bjss academy",
    author_email="academyadamin@bjss.com",
    description="Package for the Run API endpoint",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://lapetus.bjss.com/BJSS/Academy/Leeds/2018-2019/component-extraction-framework/cef",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)