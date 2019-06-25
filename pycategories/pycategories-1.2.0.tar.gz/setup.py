import os
from setuptools import setup


__this_dir = os.path.dirname(os.path.abspath(__file__))

VERSION = '1.2.0'
package_name = 'pycategories'
install_requires = [
    'infix==1.2',
]
extras_require = {
    'dev': [
        'flake8==3.6.0',
        'flake8-per-file-ignores==0.6',
        'mypy==0.670',
        'pytest',
        'pytest-cov',
    ],
    'docs': [
        'Sphinx',
        'sphinx_rtd_theme',
    ]
}
extras_require['docs'] += extras_require['dev']
setup_requires = [
    'pytest-runner',
]
tests_require = ['pytest']
packages = [
    'categories',
]
keywords = [
    'category theory',
    'monoid',
    'functor',
    'applicative',
    'monad',
    'haskell',
]
classifiers = [
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]
package_data = {
    '': ['LICENSE', 'README.rst']
}
with open(os.path.join(__this_dir, 'README.rst')) as f:
    long_description = f.read()


setup(
    name=package_name,
    packages=packages,
    version=VERSION,
    author="Daniel Hones",
    url="https://gitlab.com/danielhones/pycategories",
    description="Implementation of some concepts from category theory",
    keywords=keywords,
    classifiers=classifiers,
    license='MIT',
    install_requires=install_requires,
    extras_require=extras_require,
    package_data=package_data,
    long_description=long_description,
    setup_requires=setup_requires,
    tests_require=tests_require,
)
