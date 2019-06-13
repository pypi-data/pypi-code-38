from os.path import abspath, dirname, join

from setuptools import setup, find_packages

long_description = []

for text_file in ['README.rst', 'CHANGES.rst']:
    with open(join(dirname(abspath(__file__)), text_file), 'r') as f:
        long_description.append(f.read())

setup(
    name='traduki',
    description='SQLAlchemy internationalisation',
    long_description='\n'.join(long_description),
    version='1.2.0',
    author='Paylogic International',
    author_email='developers@paylogic.com',
    license='MIT',
    url='https://github.com/paylogic/traduki',
    install_requires=[
        'SQLAlchemy',
    ],
    packages=find_packages(exclude=['ez_setup', 'tests']),
    dependency_links=[],
    include_package_data=True,
    keywords='sqlalchemy i18n internationalisation',
)
