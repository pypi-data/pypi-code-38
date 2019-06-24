import setuptools

with open("README.MD", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="codewars", # codewars when updating to pip
    version="0.0.1",
    author="Annihilator708",
    author_email="",
    description="A toolbox for daily use",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent"
    ]
)