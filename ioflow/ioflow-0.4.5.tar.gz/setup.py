import setuptools
from setuptools import setup

setup(
    name='ioflow',
    version='0.4.5',
    packages=setuptools.find_packages(),
    setup_requires=[
        'tensorflow',
        'tokenizer_tools'
    ],
    url='https://github.com/howl-anderson/ioflow',
    license='Apache 2.0',
    author='Xiaoquan Kong',
    author_email='u1mail2me@gmail.com',
    description='Input/Output abstraction layer for machine learning',
    install_requires=['numpy', 'requests', 'flask']
)
