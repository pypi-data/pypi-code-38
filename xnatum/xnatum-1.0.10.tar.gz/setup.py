from setuptools import setup
from setuptools import find_packages

setup(
    name='xnatum',
    url='https://github.com/rgllm/xnatum',
    author='Rogerio Moreira',
    author_email='r@rgllm.com',
    packages=find_packages(),
    install_requires=['xnat', 'dicom2nifti'],
    version='1.0.10',
    license='MIT',
    description='A package for connecting and manage data on XNAT.',
)
