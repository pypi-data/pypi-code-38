import os
from setuptools import find_packages, setup


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

def _get_description():
    try:
        path = os.path.join(os.path.dirname(__file__), 'README.md')
        with open(path, encoding='utf-8') as f:
            return f.read()
    except IOError:
        return ''


setup(
    name='uk_geo_utils',
    version='0.8.0',
    author="chris48s",
    license="MIT",
    url="https://github.com/DemocracyClub/uk-geo-utils",
    packages=find_packages(),
    include_package_data=True,
    description='Django app for working with OS Addressbase, ONSUD and ONSPD',
    long_description=_get_description(),
    long_description_content_type="text/markdown",
    install_requires=[
        'Django>=1.11,<2.3',
        'psycopg2-binary',
    ],
    extras_require={
        'development': [
            'python-coveralls',
            'mkdocs',
        ]
    },
    classifiers=[
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
