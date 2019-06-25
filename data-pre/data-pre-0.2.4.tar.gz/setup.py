"""
@author: magician
@file: setup.py
@date: 2019/06/25
"""
import setuptools

DESCRIPTION = """
        # data-pre
        pandas data preprocessing
        
        ### Use pandas to preprocess data tool.support excel, csv, json, pickle different IO format data read and write
        
        * read file(excel, json, pickle)
        * write file
        * DataFrame preview
        * DataFrame drop
        * DataFrame select
        * DataFrame style
        * DataFrame preprocessing
        * DataFrame statistics
        * DataFrame pivot
        * DataFrame total
        * Multi-index DataFrame downgrade
"""

setuptools.setup(
    name="data-pre",
    version="0.2.4",
    author="magician",
    author_email="ftconan@163.com",
    description="pandas data preprocessing tool",
    long_description=DESCRIPTION,
    long_description_content_type="markdown",
    url="https://github.com/ftconan/data_pre.git",
    packages=setuptools.find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[
        'pandas',
        'numpy'
    ]
)
