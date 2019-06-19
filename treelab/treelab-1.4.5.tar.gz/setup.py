from setuptools import setup, find_packages
import treelab

"""
python setup.py bdist_wheel 
python setup.py sdist 
twine upload dist/*
"""
setup(
    name=treelab.__name__,
    version=treelab.__version__,
    packages=find_packages(exclude=["tests"]),
    install_requires=['Rx>=3.0.0a3', 'grpcio>=1.20.0', 'grpcio-tools>=1.20.0', 'pandas>=0.24.2'],
    python_requires='>=3',
    zip_safe=True,
    license='BSD License',
    url=treelab.__url__,
    long_description='The Treelab Python API provides an easy way to integrate Treelab with any external system. The API closely follows REST semantics, uses JSON to encode objects, and relies on standard HTTP codes to signal operation outcomes.'
)
