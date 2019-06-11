from glob import glob
from setuptools import setup, find_packages

setup(
    name='ppts',
    version='1.0.28',
    description='ppt with web',
    author='simdd',
    author_email='dev.simdd@gmail.com',
    packages=find_packages(),
    scripts=['bin.py'],
    data_files=[('ppts', glob('web/**'))],
    entry_points={
        'console_scripts': [
            'ppts = bin:main',
        ]
    }
)
