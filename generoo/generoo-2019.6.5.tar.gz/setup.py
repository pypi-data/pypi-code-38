import os
import sys
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

archetype_filenames = []
examples_filenames = []

for root, dirs, files in os.walk("generoo/archetypes", topdown=False):
    for f in files:
        if f is not None:
            archetype_filenames.append(os.path.join(root[len("generoo/"):], f))

for root, dirs, files in os.walk("generoo/examples", topdown=False):
    for f in files:
        if f is not None:
            examples_filenames.append(os.path.join(root[len("generoo/"):], f))

package_data = {"generoo":  archetype_filenames + examples_filenames}

setuptools.setup(
    name="generoo",
    version="2019.06.05",
    author="Thomas Sickert",
    author_email="thomas.sickert@gmail.com",
    description="Generate code without writing any.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/army-of-one/generoo",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=[
        "altgraph==0.16.1",
        "future==0.17.1",
        "macholib==1.11",
        "pefile==2019.4.18",
        "pick==0.6.4",
        "PyInstaller==3.4",
        "pystache==0.5.4",
        "PyYAML==5.1",
        "regex==2019.06.05",
    ],
    package_data=package_data,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
