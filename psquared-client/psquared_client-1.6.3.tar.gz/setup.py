"""A setuptools based setup module.

See:
https://gitlab.com/nest.lbl.gov/psquared
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path
# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='psquared_client',  # Required
    version='1.6.3',  # Required
    description='Manage the connection and communications to a PSquared server.',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='http://nest.lbl.gov/projects/psquared',  # Optional
    author='Simon Patton',  # Optional
    author_email='sjpatton@lbl.gov',  # Optional
    classifiers=[  # Optional
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    #keywords='keyword1 keyword2',  # Optional
    packages=['psquared_client'],  # Required
    py_modules=['pp_cli'],  # Optional
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4',
    install_requires=['requests'],  # Optional
    entry_points={  # Optional
        'console_scripts': [
            'pp-cli=pp_cli:main',
        ],
    }
)
