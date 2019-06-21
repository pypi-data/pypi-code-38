"""weeder - remove unneeded historical files.
"""

from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='weeder',
    version='0.1',
    description='Remove unneeded historical files',
    long_description=long_description,
    url='https://github.com/GambitResearch/weeder',
    author='Daniele Varrazzo',
    author_email='piro@gambitresearch.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='backup sysadmin junk',
    py_modules=["weeder"],
    python_requires='>=3.4, <4',
    entry_points={'console_scripts': ['weeder=weeder:main']},
    project_urls={
        'Bug Reports': 'https://github.com/GambitResearch/weeder/issues',
        'Source': 'https://github.com/GambitResearch/weeder/',
    },
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)
