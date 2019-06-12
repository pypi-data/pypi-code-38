from pathlib import Path
from setuptools import find_packages, setup

readme = Path('README.rst').read_text(encoding="utf-8")
history = Path('docs/history.rst').read_text(encoding="utf-8")

runtime_requirements = [
    'Click'
]
development_requirements = [
    'pip>=19.0.2',
    'bumpversion>=0.5.3',
    'wheel>=0.32.3',
    'watchdog>=0.9.0',
    'flake8>=3.6.0',
    'tox>=3.6.1',
    'coverage>=4.5.2',
    'Sphinx>=1.8.3',
    'twine>=1.12.1',
    'pluggy>=0.7.0',
    'mypy>=0.650',
    'pytest>=3.8.2',
    'pytest-runner>=4.2',
    'pytest-mock>=1.10.1',
]

setup(
    author="Thomas Jahoda",
    author_email="thomasjahoda@users.noreply.github.com",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="",
    install_requires=runtime_requirements,
    extras_require={
        'dev': development_requirements
    },
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='tjpy_click_util',
    name='tjpy_click_util',
    packages=find_packages(include=['tjpy_click_util', 'tjpy_click_util.*']),
    test_suite='tests',
    url='https://github.com/thomasjahoda/tjpy_click_util',
    version='0.1.1',
    zip_safe=False,
)
