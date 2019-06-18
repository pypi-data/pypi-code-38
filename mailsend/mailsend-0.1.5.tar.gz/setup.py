from setuptools import setup
import os
import re

VERSIONFILE = "mailsend.py"


def get_version():
    with open(VERSIONFILE, 'rb') as f:
        return re.search("^__version__\s*=\s*['\"]([^'\"]*)['\"]",
                           f.read().decode('UTF-8'), re.M).group(1)


def read(*path):
    """
    Return content from ``path`` as a string
    """
    with open(os.path.join(os.path.dirname(__file__), *path), 'rb') as f:
        return f.read().decode('UTF-8')

setup(
    name='mailsend',
    version=get_version(),
    url='https://bitbucket.org/ollyc/mailsend',
    license='BSD',
    author='Oliver Cope',
    author_email='oliver@redgecko.org',
    description='Fork of tinysmtp with bug fixes and python 3 compatibility',
    long_description=read('README.rst') + "\n\n" + read("CHANGELOG.rst"),
    py_modules=['mailsend'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=['envparse>=0.2'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
