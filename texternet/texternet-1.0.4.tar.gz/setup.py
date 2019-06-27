import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="texternet",
    version="1.0.4",
    author="Kyle Henry",
    author_email="kylehenry@texternet.com",
    description="Package for interacting with and developing apps for Texternet.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SonicHedghog/Texternet",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['twilio'],
)