"""
@author: magician
@file: setup.py
@date: 2019/06/25
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="data-pre",
    version="0.1.7",
    author="magician",
    author_email="ftconan@163.com",
    description="pandas data preprocessing tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ftconan/data_pre.git",
    packages=setuptools.find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[
        'pandas',
        'numpy'
    ]
)
