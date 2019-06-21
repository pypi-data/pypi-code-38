from setuptools import setup, find_packages

VERSION = '0.6.1'

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='cockatoo',
    description='cockatoo - A similarity metric for macromolecular crystallization conditions',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Andrew E. Bruno',
    url='https://github.com/ubccr/cockatoo',
    license='GNU General Public License v3 (GPLv3)',
    author_email='aebruno2@buffalo.edu',
    version=VERSION,
    include_package_data=True,
    packages=find_packages(exclude=['tests*']),
    package_data={'cockatoo': ['data/*.csv', 'data/*.json']},
    install_requires=[
        'Click',
        'e3fp',
        'marshmallow>=2.15.1',
        'numpy',
        'scipy',
        'matplotlib',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        cockatoo=cockatoo.cli:main
    ''',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
     ]
)
