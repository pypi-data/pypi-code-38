from setuptools import setup

setup(
    name='ophardtimport',
    version='1.1',
    packages=['ophardtImport'],
    url='https://github.com/Phill93/ophardtimport',
    license='GPLv3',
    author='Phill93',
    author_email='phill93@phill93.de',
    description='Allows python to interact with Ophardt file exports',
    install_requires=[
        'xmltodict',
        'pillow'
    ]
)
