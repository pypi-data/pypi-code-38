
from setuptools import setup, find_packages
from netlookup.version import __version__

setup(
    name='netlookup',
    keywords='network subnet lookup utilities',
    description='python tools to look up information about networks',
    author='Ilkka Tuohela',
    author_email='hile@iki.fi',
    url='https://github.com/hile/netlookup/',
    version=__version__,
    license='PSF',
    packages=find_packages(),
    python_requires='>3.6.0',
    entry_points={
        'console_scripts': [
            'netlookup=netlookup.bin.netlookup:main',
        ],
    },
    install_requires=(
        'dnspython',
        'netaddr',
        'requests',
        'systematic>=4.8.6',
    ),
    tests_require=(
        'pytest',
        'pytest-runner',
        'pytest-datafiles',
    ),
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3',
        'Topic :: System',
        'Topic :: System :: Systems Administration',
    ],
)
