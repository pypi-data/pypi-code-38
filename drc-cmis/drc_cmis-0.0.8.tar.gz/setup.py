from io import open

from setuptools import find_packages, setup

with open('drc_cmis/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.0.1'

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

REQUIRES = [
    "django_choices", "django", "cmislib-maykin", "django-solo"
]

setup(
    name='drc_cmis',
    version=version,
    description='A CMIS backend for gemma-documentregistratiecomponent',
    long_description=readme,
    author='Jorik Kraaikamp',
    author_email='jorikkraaikamp@gmail.com',
    maintainer='Jorik Kraaikamp',
    maintainer_email='jorikkraaikamp@gmail.com',
    url='https://github.com/gemeenteutrecht/drc_cmis',
    license='MIT',

    keywords=[
        '',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        "Framework :: Django",
    ],

    install_requires=REQUIRES,
    tests_require=['coverage', 'pytest'],

    packages=find_packages(),
)
