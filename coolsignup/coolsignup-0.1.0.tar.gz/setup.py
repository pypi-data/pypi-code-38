from setuptools import setup
from glob import glob

with open('README.md') as fd:
    long_description = fd.read()

locale_files = [path[len('coolsignup/'):] for path in glob('coolsignup/locale/*/*/*.[mp]o')]
package_data = {'coolsignup': ['locale/coolsignup.pot'] + locale_files}

setup(
    name='coolsignup',
    version='0.1.0',
    python_requires='>=3.5.2',
    install_requires = [
        'tornado>=6.0.2',
        'motor>=2.0.0',
        'pymongo>=3.8.0',
        'bcrypt>=3.1.6',
        'passlib>=1.7.1',
        'zxcvbn>=4.4.28',
        'naval>=1.0.0',
        'postpone>=0.3.0'
    ],
    packages=['coolsignup'],
    package_data = package_data,
    include_package_data = True,
    scripts=['bin/coolsignup'],
    author = 'Benjamin Le Forestier',
    author_email = 'benjamin@leforestier.org',
    keywords = [
        "signup", "signin", "user", "accounts", "email", "registration"
    ],
    description = (
        "REST-like server to register users by email and handle login, logout, authentication, email changes and password reset."
    ),
    long_description = long_description,
    classifiers = [
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ]
)
