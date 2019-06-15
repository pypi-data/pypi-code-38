'''
PyPi setup script.
'''

import setuptools

from angda import VERSION_NUMBER

LONG_DESC = open('readme.md').read()

setuptools.setup(
    # Basic information.
    name         = 'angda',
    version      = VERSION_NUMBER,
    author       = 'Stephen Malone',
    author_email = 'mail@angda.org',
    description  = 'A neat generic dice API.',
    url          = 'https://angda.org',

    # Long descriptions.
    long_description              = LONG_DESC,
    long_description_content_type = 'text/markdown',

    # Package details.
    packages = setuptools.find_packages(exclude=['tests*']),
    zip_safe = True,

    # Classifiers.
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Games/Entertainment',
    ],

    # Program entry points.
    entry_points = {
        'console_scripts': ['angda=angda.__main__:main'],
    },

    # Project URLs.
    project_urls = {
        'Repository':  'https://bitbucket.org/angda/angda',
        'Bug Tracker': 'https://bitbucket.org/angda/angda/issues?status=new&status=open',
    },
)
