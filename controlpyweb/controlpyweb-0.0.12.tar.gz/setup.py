import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="controlpyweb",
    version="0.0.12",
    author="Steve Jackson",
    author_email="washad@gmail.com",
    description="A project to facilitate easy read/write to the ControlByWeb line of Automation/SCADA IO products.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/washad/ControlPyWeb",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
