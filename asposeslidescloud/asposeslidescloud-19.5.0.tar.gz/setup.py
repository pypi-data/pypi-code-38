import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="asposeslidescloud",
    version="19.5.0",
    author="Victor Putrov",
    author_email="vistor.putrov@aspose.com",
    description="Aspose.Slides Cloud SDK for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    install_requires=[ "urllib3 >= 1.15.1", "six >= 1.10", "certifi >= 14.05.14" ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)