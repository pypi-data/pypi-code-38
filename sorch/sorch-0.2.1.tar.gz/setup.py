try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

long_desc = '''Simple PyTorch utils, yet another package.
This one is mostly for my personal applications.'''

# python setup.py sdist bdist_wheel
# twine upload dist/*
setup(
    name='sorch',
    version='0.2.1',
    packages=['sorch', 'sorch.trainer'],
    url='https://github.com/PiotrDabkowski/sorch',
    install_requires=['torch>=0.4', 'six>=1.11', 'tensorboardX>=1.0'],
    license='MIT',
    author='Piotr Dabkowski',
    author_email='piodrus@gmail.com',
    description='Simple PyTorch utils, yet another package :)',
    long_description=long_desc)
