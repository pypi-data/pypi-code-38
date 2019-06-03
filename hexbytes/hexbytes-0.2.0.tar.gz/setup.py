#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import (
    setup,
    find_packages,
)

extras_require = {
    'test': [
        "pytest>=3.6.0",
        "pytest-xdist",
        "tox>=2.9.1,<3",
        "hypothesis>=3.44.24,<4",
        "eth-hash[pycryptodome]",
    ],
    'lint': [
        "flake8==3.4.1",
        "isort>=4.2.15,<5",
        "mypy==0.701",
        "pydocstyle>=3.0.0,<4",
    ],
    'doc': [
        "Sphinx>=1.6.5,<2",
        "sphinx_rtd_theme>=0.1.9",
    ],
    'dev': [
        "bumpversion>=0.5.3,<1",
        "pytest-watch>=4.1.0,<5",
        "wheel",
        "twine",
        "ipython",
    ],
}

extras_require['dev'] = (
    extras_require['dev'] +  # noqa: W504
    extras_require['test'] +  # noqa: W504
    extras_require['lint'] +  # noqa: W504
    extras_require['doc']
)


with open('./README.md') as readme:
    long_description = readme.read()


setup(
    name='hexbytes',
    # *IMPORTANT*: Don't manually change the version here. Use `make bump`, as described in readme
    version='0.2.0',
    description="""hexbytes: Python `bytes` subclass that decodes hex, with a readable console output""",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='The Ethereum Foundation',
    author_email='snakecharmers@ethereum.org',
    url='https://github.com/ethereum/hexbytes',
    include_package_data=True,
    install_requires=[
        'eth-utils>=1.0.1,<2',
    ],
    python_requires='>=3.6, <4',
    extras_require=extras_require,
    py_modules=['hexbytes'],
    license="MIT",
    zip_safe=False,
    keywords='ethereum',
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={'hexbytes': ['py.typed']},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
