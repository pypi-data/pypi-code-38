import os
import io

from setuptools import setup, find_packages

metadata = {}

# Required modules
required = [
    'requests>=2.21.0',
]

# Get working directory
cur_dir = os.path.abspath(os.path.dirname(__file__))

# Get README content
with io.open(os.path.join(cur_dir, 'README.md'), mode='r', encoding='utf-8') as f:
    long_description = '\n' + f.read()

# Get project version
with io.open(os.path.join(cur_dir, 'slipo', '__version__.py'), mode='r', encoding='utf-8') as f:
    exec(f.read(), metadata)

setup(
    name='slipo',
    version=metadata['__version__'],
    author='Yannis Kouvaras',
    author_email='jkouvar@imis.athena-innovation.gr',
    license='Apache Software License',
    description='SLIPO API Python client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/SLIPO-EU/slipo-python',
    packages=find_packages(),
    python_requires='>=3',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    install_requires=required,
    keywords='poi linked-data point-of-interest data-integration',
    test_suite='nose.collector',
    tests_require=['nose'],
)
