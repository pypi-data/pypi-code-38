import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="orionframework",
    version="1.0.3",
    author="Orion Framework",
    author_email="orionframework@gmail.com",
    description="A python companion library for the Orion Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="...",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
