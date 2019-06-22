# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="MapCoords",
    version="0.1.7",
    description="A Python library about map coordinations",
    long_description=open('README.rst').read(),
    author='Ijustwantyouhappy',
    author_email='18817363043@163.com',
    maintainer='',
    maintainer_email='',
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    package_data = {
        '': ['*.hdf5', '*.html', '*.ipynb', '*.jpg', '*.npz']
    },
    platforms=["all"],
    url='',
    install_requires=["numpy>=1.14.2", 
                      "scipy>=1.1.0", 
                      "pandas>=0.22.0", 
                      "matplotlib>=2.0.2", 
                      "h5py>=2.8.0", 
                      "requests>=2.14.2"],
    classifiers=[
        "Environment :: Web Environment",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Programming Language :: Python :: 3.5',
    ]
)