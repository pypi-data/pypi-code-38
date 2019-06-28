# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='soba',
    version='4.0',
    description='Simulator of Occupancy Based on Agent',
    url='https://github.com/gsi-upm/soba',
    author='GSI - UPM',
    author_email='eduardo.merinom13@gmail.com',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='simulation agents crowds',
    packages=['soba', 'soba/agents', 'soba/agents/resources', 'soba/launchers', 'soba/models', 'soba/space', 'soba/visualization', 'soba/visualization/ramen', 'soba/visualization/lib'],
    package_data={'soba': ['visualization/favicon.ico', 'visualization/lib/*.js', 'visualization/*.html', 'visualization/*.js']},
    install_requires=['numpy', 'anaconda-client','tqdm','mesa', 'transitions', 'tornado==4.5.3', 'pandas'],
    python_requires='>=3',
)

