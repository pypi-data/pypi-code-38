import os
import subprocess

from setuptools import setup, find_packages


def read_file(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8').read()


def git_version():
    """
    Fetch version from git information
    """
    git_default_version = '0.1.0'
    try:
        git_tag = subprocess.check_output(['git', 'describe', '--tags'])
        if git_tag:
            return git_tag.strip()[1:].decode('utf-8')
    except Exception:
        return git_default_version


setup(
    name="cocktail-apikit",

    version=git_version(),

    description="A collection of tools for APIs",
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',

    url='http://gitlab.com/theo-l/cocktail_apikit',

    author='Liang Guisheng',
    author_email='theol.liang@truckpad.com.br',

    license='MIT',

    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],

    keywords='cocktail_apikit backend apikit',

    packages=["cocktail_apikit"],

    install_requires=read_file('requirements.txt').strip().split('\n')[1:],

    extras_require={
        'dev': read_file('requirements-dev.txt').strip().split('\n')[1:]
    }

)
