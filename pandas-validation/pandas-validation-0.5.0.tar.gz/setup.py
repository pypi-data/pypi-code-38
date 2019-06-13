from setuptools import setup, find_packages
from os.path import join, dirname


setup(
    name='pandas-validation',
    version='0.5.0',
    description=(
        'A Python package for validating data with pandas'),
    long_description=open(
        join(dirname(__file__), 'README.rst'), encoding='utf-8').read(),
    packages=find_packages(exclude=['docs', 'tests*']),
    py_modules=['pandasvalidation'],
    install_requires=['pandas>=0.22'],
    author='Markus Englund',
    author_email='jan.markus.englund@gmail.com',
    url='https://github.com/jmenglund/pandas-validation',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'],
    keywords=['pandas', 'validation'],
)
