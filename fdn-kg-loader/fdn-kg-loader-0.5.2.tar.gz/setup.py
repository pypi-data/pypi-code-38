import setuptools

setuptools.setup(
    name='fdn-kg-loader',
    version='0.5.2',
    packages=setuptools.find_packages(),
    license='Restricted License, FDN license',
    long_description=open('README.txt').read(),
    entry_points={
        'console_scripts': ['fdn_kg_loader=fdn_kg_loader:main']
    },
    install_requires=[
        'grpcio',
        'protobuf',
        'grakn',
        'grakn-client',
        'click',
        'six'
    ]
)
