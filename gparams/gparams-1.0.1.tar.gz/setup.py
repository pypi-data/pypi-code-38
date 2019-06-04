# -*- coding: utf-8 -*-

import os

try:
    import setuptools
except ImportError:
    import distutils.core as setuptools


here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(here, 'gparams', '__about__.py'), 'r') as f:
    exec(f.read(), about)

__VERSION__ = about['VERSION']

requirements = [
    'PyYAML==3.13',
    'Jinja2==2.10'
]

test_requirements = ['mock']

with open("README.md", "r") as fh:
    long_description = fh.read()

packages = setuptools.find_packages(exclude=['tests', 'venv'])
setuptools.setup(
    name='gparams',
    description="A kit to process the parameters of the GeneDock workflow (help for batch delivery).",
    version=__VERSION__,
    author='Rao Mengnan',
    author_email="raomengnan@genedock.com",
    maintainer='GeneDock Contributor',
    maintainer_email='raomengnan@genedock.com',
    url='https://www.genedock.com',
    packages=packages,
    package_data={'': ['LICENSE', 'requirements.txt']},
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Customer Service',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    entry_points={
        'console_scripts': [
            'gparams = gparams:entry',
        ]
    },
    platforms=['Independent'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    tests_require=test_requirements,
    test_suite='tests'
)
