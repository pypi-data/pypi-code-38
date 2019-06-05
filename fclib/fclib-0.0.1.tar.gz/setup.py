import setuptools
import io
import re
from glob import glob
from os.path import splitext, basename, join, dirname


with open("README.org", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fclib",
    version="0.0.1",
    license="BSD 3-Clause License",
    author="André Sabino",
    author_email="andre.sabino@gmail.com",
    description="A financial computation library",
    long_description=long_description,
    long_description_content_type="text/plain",
    url="https://github.com/amgs/fclib",
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'scipy',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
)
