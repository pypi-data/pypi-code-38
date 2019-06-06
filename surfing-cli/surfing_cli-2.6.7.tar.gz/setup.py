from setuptools import setup, find_packages
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="surfing_cli",
    version="2.6.7",
    author="Babbage",
    author_email="babbage@hotmail.com",
    description="冲浪科技专用脚本库",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/uighurbabbage",
    packages=find_packages(),
    install_requires=[
        "Click",
        "xlwt",
        "pycrypto",
        "chardet",
        "fabric"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    data_files=[
        (os.path.expanduser('~'), ['skeleton_configs/surfing.conf.example.json'])
    ],
    entry_points='''
        [console_scripts]
        surfing_cli=cli.entry:cli
        surfing_ftpserver_cli=cli.entry:ftp_server_cli
    '''
)
