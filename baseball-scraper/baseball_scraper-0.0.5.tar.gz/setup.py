from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='baseball_scraper',
    version='0.0.5',
    description='Retrieve baseball data in Python',
    long_description=long_description,
    url='https://github.com/spilchen/baseball_scraper',
    author='Matt Spilchen',
    author_email='matt.spilchen@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='baseball sabermetrics data statistics statcast web scraping',
    packages=['baseball_scraper'],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    install_requires=['numpy>=1.13.0',
                      'pandas >= 0.20.2',
                      'beautifulsoup4>=4.4.0',
                      'requests>=2.18.1',
                      'lxml>=4.2.1'
                      ],
)
