import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

with open('requirements.txt', 'r') as f:
    reqs = f.read()
requirements = [req for req in reqs.split('\n') 
                    if req != '' and not req.startswith('#')]

long_description_content_type = 'text/markdown'

name = 'bootcamp_utils'
version = '0.0.3'
author = 'Justin Bois'
author_email = 'bois@caltech.edu'
url = 'https://github.com/justinbois/bootcamp_utils'
install_requires = requirements
description = ('Utilities for use in the Introduction to Programming in the' 
                + ' Biological Sciences Bootcamp.')

setuptools.setup(
    name=name,
    version=version,
    author=author,
    author_email=author_email,
    url=url,
    install_requires=requirements,
    description=description,
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
)
