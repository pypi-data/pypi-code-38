import os

from setuptools import setup

VERSION_FILE = 'VERSION'
version = '0.1+local'
if os.path.isfile(VERSION_FILE):
    with open(VERSION_FILE, 'r') as f:
        version = f.read()

install_requires = ['Click==7.0', 'requests==2.22']

setup(
    name='cancergeonomics',
    version=version,
    py_modules=['cancergeonomics'],
    install_requires=install_requires,
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    platforms=['Windows', 'POSIX', 'MacOS'],
    author='Stefan Milutinovic',
    author_email='stefan@milutinovic.com',
    url='https://github.com/sbg/sevenbridges-python',
    download_url='https://github.com/Milutinke92/cancergeonomics/archive/master.zip',
    license='MIT License',
    entry_points='''
        [console_scripts]
        cgccli=cancergeonomics.cli:cgccli
    ''',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
