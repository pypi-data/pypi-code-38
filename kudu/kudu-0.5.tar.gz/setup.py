from setuptools import setup, find_packages

from kudu import __author__
from kudu import __email__
from kudu import __version__

setup(
    name='kudu',
    author=__author__,
    author_email=__email__,
    version=__version__,
    description='A deployment command line program in Python.',
    url='https://github.com/torfeld6/kudu',
    license='BSD',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='cli',
    packages=find_packages(),
    install_requires=['requests>=2.20.1', 'PyYAML', 'GitPython', 'watchdog', 'click'],
    entry_points={
        'console_scripts': [
            'kudu = kudu.__main__:cli',
        ],
    },
)
