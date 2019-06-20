import setuptools

setuptools.setup(
    name='fdn-kg-loader',
    version='0.1.1',
    packages=setuptools.find_packages(),
    license='Restricted License, FDN license',
    long_description=open('README.txt').read(),
    entry_points={
        'console_scripts': ['fdnloader=fdnloader:main']
    },
    install_requires=[
        'grpcio==1.16.0',
        'protobuf==3.6.1',
        'grakn',
        'grakn-client',
        'click',
        'six==1.11.0'
    ]
)
