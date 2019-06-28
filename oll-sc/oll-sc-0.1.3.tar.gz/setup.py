from setuptools import find_packages, setup

PACKAGE_NAME = 'oll-sc'
VERSION = '0.1.3'
AUTHOR = 'Open Law Library'
AUTHOR_EMAIL = 'info@openlawlib.org'
DESCRIPTION = 'Wrapper around PyKCS11 and openSC used to create smart card signatures'
URL = 'https://github.com/platform/oll-sc/tree/master'

with open('README.md', encoding='utf-8') as file_object:
  long_description = file_object.read()

packages = find_packages()

ci_require = [
    "pylint==2.3.1",
    "bandit==1.6.0",
    "pytest==4.5.0",
    "pytest-cov==2.7.1"
]

dev_require = [
    "autopep8==1.4.4",
    "pylint==2.3.1",
    "bandit==1.6.0"
]

tests_require = [
    "pytest==4.5.0"
]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=packages,
    include_package_data=True,
    data_files=[
        ('lib/site-packages/oll_sc', [
            './LICENSE.txt',
            './README.md'
        ])
    ],
    zip_safe=False,
    install_requires=[
        'click==6.7',
        'cryptography>=2.3.1',
        'PyKCS11==1.5.5',
        'yubikey-manager',
    ],
    extras_require={
        'ci': ci_require,
        'dev': dev_require,
        'test': tests_require
    },
    tests_require=tests_require,
    entry_points={
        'console_scripts': [
            'oll-sc = oll_sc.cli:oll_sc'
        ]
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Security',
        'Topic :: Software Development',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ]
)
