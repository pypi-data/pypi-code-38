import imp
import os
import setuptools

version = imp.load_source(
    "usps_client.version", os.path.sep.join(["src", "usps_client", "version.py"])
)

with open("README.md") as fh:
    long_description = fh.read()

with open("requirements.txt") as fh:
    install_requires = fh.read()

setuptools.setup(
    name="usps-client",
    version=version.VERSION,  # type: ignore
    author="Micah Denbraver",
    author_email="macromicah@gmail.com",
    description="An unofficial client for the USPS Web Tools APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/macro1/usps-client",
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    data_files=[("requirements", ["requirements.txt"])],
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
