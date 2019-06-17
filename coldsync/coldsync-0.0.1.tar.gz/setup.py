import setuptools
from distutils.core import setup

testpkgs = [
    "pytest",
    "pytest-cov<2.6",
    "pytest-runner",
    "python-coveralls"
]

setup(
    name='coldsync',
    version='0.0.1',
    description='Used to upload file sto cold storage',
    author='Andrei Neagu',
    author_email='it.neagu.andrei@gmail.com',
    packages=['coldsync'],
    license='GPLv3',
    install_requires=[
        "google==2.0.2",
        "google-cloud-storage==1.16.1",
        'Click==7.0',
    ],
    entry_points={
        'console_scripts': [
            'coldsync = coldsync.main:main'
        ]
    },
    tests_require=testpkgs,
    extras_require={
        'testing': testpkgs
    },
    setup_requires=['pytest-runner'],
    classifiers=[
        "Topic :: System :: Archiving",
        "Topic :: System :: Archiving :: Backup",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: PyPy"
    ]
)
