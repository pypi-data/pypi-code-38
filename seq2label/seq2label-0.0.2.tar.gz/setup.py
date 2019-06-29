import setuptools
from setuptools import setup

setup(
    name='seq2label',
    version='0.0.2',
    packages=setuptools.find_packages(),
    url='https://github.com/howl-anderson/seq2label',
    include_package_data=True,
    license='Apache 2.0',
    author='Xiaoquan Kong',
    author_email='u1mail2me@gmail.com',
    description='seq2label',
    install_requires=['tensorflow', 'flask', 'flask-cors', 'ioflow']
)
