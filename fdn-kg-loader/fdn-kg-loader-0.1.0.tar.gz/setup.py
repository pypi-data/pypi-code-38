import setuptools

setuptools.setup(
    name='fdn-kg-loader',
    version='0.1.0',
    packages=setuptools.find_packages(),
    license='Restricted License, FDN license',
    long_description=open('README.txt').read(),
    entry_points={
        'console_scripts': ['fdnloader=fdnloader:main']
    }
)
