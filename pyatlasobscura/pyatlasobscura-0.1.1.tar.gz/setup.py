from setuptools import find_packages, setup

setup(
    name='pyatlasobscura',
    version='0.1.1',
    packages=find_packages(),
    python_requires='>=3.6.0',
    url='https://github.com/drewsonne/pyatlasobscura',
    license='LGPLv3',
    author='Drew J. Sonne',
    author_email='drew.sonne@gmail.com',
    description='',
    install_requires=[
        'requests',
        'beautifulsoup4',
        'latlon'
    ],
    extras_require={
        'pandas': ['pandas']
    }
)
