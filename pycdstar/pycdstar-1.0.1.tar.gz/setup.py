from setuptools import setup, find_packages

setup(
    name='pycdstar',
    version="1.0.1",
    description='A python wrapper for the CDStar API',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    author='Robert Forkel',
    author_email='forkel@shh.mpg.de',
    url='https://github.com/clld/pycdstar',
    license="Apache 2",
    zip_safe=False,
    keywords='',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        'console_scripts': [
            "cdstar = pycdstar.__main__:main"
        ]
    },
    install_requires=[
        'docopt',
        'requests',
        'AppDirs',
        'python-dateutil',
        'unidecode',
    ],
    extras_require={
        'dev': [
            'tox',
            'flake8',
            'wheel',
            'twine',
        ],
        'test': [
            'mock',
            'pytest>=3.6',
            'pytest-mock',
            'pytest-cov',
            'coverage>=4.2',
            'httmock',
        ],
    })
