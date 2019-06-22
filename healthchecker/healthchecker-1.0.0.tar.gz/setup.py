#!/usr/bin/env python3

"""HealthChecker installer script.

Install with `setup.py install`.
"""

from setuptools import setup

from healthchecker.__init__ import __version__


def _readme():
    with open('README.md') as readme:
        return readme.read()


setup(
    name='healthchecker',
    version=__version__,
    description='Check sites health and publish results in a file in Github',
    long_description=_readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later '
        '(GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: System :: Monitoring',
        'Topic :: Utilities',
        'Typing :: Typed',
    ],
    platforms=[
      'POSIX :: Linux'
    ],
    keywords='check ping response monitoring',
    url='https://git.rlab.be/sysadmins/healthchecker',
    download_url='https://git.rlab.be/sysadmins/healthchecker/releases',
    author='HacKan',
    author_email='hackan@rlab.be',
    license='GPLv3+',
    packages=['healthchecker'],
    python_requires='>=3.7',
    install_requires=[
        'PyGithub~=1.43',
        'requests~=2.21',
    ],
    entry_points={
        'console_scripts': ['healthchecker=healthchecker.__main__:run'],
    },
    zip_safe=True,
)
