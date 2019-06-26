import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="parinya",
    version="0.0.27",
    author="Parinya Sanguansat",
    author_email="sanguansat@yahoo.com",
    description="A collection of my codes",
    long_description="A collection of my codes",
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=['numpy'],
)
