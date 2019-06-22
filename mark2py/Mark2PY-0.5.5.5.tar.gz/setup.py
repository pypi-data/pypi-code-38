import setuptools
import os

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="Mark2PY",
    version="0.5.5.5",
    author="AMJoshaghani",
    author_email="amjoshaghani@gmail.com",
    description="this package help developers to write Markdown & Markup in python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amjoshaghani/Mark2PY",
    license='MIT',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["mistune"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
