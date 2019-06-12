from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='pyvasa',
    version='1.0',
    author='Hannes Ebelt',
    author_email='hannes.ebelt@sap.com',
    description='Python package for NetApp VASA Appliance',
    url='https://github.com/sapcc/vasa/pyvasa',
    packages=find_packages(),
    install_requires=[
        'packaging>=16.8',
        'requests>=2.18.1',
        'urllib3>=1.21.1'
        ],
    classifiers=["Programming Language :: Python :: 3"],
    )
