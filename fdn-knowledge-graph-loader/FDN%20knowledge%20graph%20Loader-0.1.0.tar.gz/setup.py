import setuptools

setuptools.setup(
    name='FDN knowledge graph Loader',
    version='0.1.0',
    packages=setuptools.find_packages(),
    license='Restricted License, FDN license',
    long_description=open('README.txt').read(),
    entry_points={
        'console_scripts': ['fdnloader=fdnloader:main']
    }
)
