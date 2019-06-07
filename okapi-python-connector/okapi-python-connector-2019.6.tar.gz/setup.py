import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="okapi-python-connector",
    version="v2019.06",
    author="Jonas Radtke",
    author_email="jonas@okapiorbits.space",
    description="Package to connect to OKAPI Api",
    long_description="For full information on the package, including a small tutorial and an api documentation, go to www.okapiorbits.space/documentation",
    long_description_content_type="text/markdown",
    url="https://github.com/OKAPIOrbits/OkapiPythonConnector",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
