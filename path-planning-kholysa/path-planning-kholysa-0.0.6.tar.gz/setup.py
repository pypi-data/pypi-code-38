import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="path-planning-kholysa",
    version="0.0.6",
    author="Saif Elkholy",
    author_email="saif.elkholy@mail.mcgill.com",
    description="A package using the A* algorithm to plan a path for a quadcopter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)