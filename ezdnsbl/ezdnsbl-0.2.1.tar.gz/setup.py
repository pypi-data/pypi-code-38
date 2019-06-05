#!/usr/bin/var python
# -*- coding: utf-8 -*-

from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

try:
    from ezdnsbl.version import __version__
except ImportError:
    pass

exec(open('ezdnsbl/version.py').read())


setup(
    name='ezdnsbl',
    version=__version__,
    description='Easy DNSBL querying',
    long_description=readme(),
    long_description_content_type='text/x-rst',
    author='c0nch0b4r',
    author_email='lp1.on.fire@gmail.com',
    packages=[
        'ezdnsbl',
        'ezdnsbl.provider'
    ],
    entry_points={
        'console_scripts': [
            'ezdnsbl-query=ezdnsbl.query:main'
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
        'Topic :: Security'
    ],
    keywords='dnsbl blacklist dns',
    url='https://bitbucket.org/c0nch0b4r/ezdnsbl/',
    download_url='https://bitbucket.org/c0nch0b4r/ezdnsbl/get/' + __version__ + '.tar.gz',
    project_urls={
        'Source': 'https://bitbucket.org/c0nch0b4r/ezdnsbl/'
    },
    python_requires='~=2.7',
    install_requires=[
        'dnspython'
    ]
)
