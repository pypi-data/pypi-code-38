# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, '', 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='BatchAdapt',

    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.22',

    description='Wrapper for easily running cutadapt in batch from a CLI.',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/helloabunai/BatchAdapt',

    # Author details
    author='Alastair Maxwell/University of Glasgow',
    author_email='alastair.maxwell@glasgow.ac.uk',

    # License to ship the package with
    license='GPLv3',

    # More information?
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
	# 2 - Pre-Alpha
	# 3 - Alpha
	# 4 - Beta
	# 5 - Stable
	classifiers=[
		'Development Status :: 2 - Pre-Alpha',

		# Indicate who your project is intended for
		'Intended Audience :: Education',
		'Intended Audience :: End Users/Desktop',
		'Intended Audience :: Science/Research',

		# Classifier matching license flag from above
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

		# Specific version of the python interpreter that are supported
		# by this package. Python 3 not support at this time.
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',

		## And so on
		'Environment :: Console',
		'Operating System :: MacOS :: MacOS X',
		'Operating System :: POSIX'
	],

    # What does the project relate to?
    keywords='Cutadapt Demultiplexing FastQ Sequences Batch',

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['progressbar2'],

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['input',
									'lib',
									'batchadapt.egg-info',
									'build',
									'dist',
									'logs'
									]),

	# Executable scripts require an entry point to allow cython to generate
	# executables for the respective target platform. This entry point is akin
	# to launching the script in bash: if __name__ == '__main__' etc..
    entry_points={
        'console_scripts': ['batchadapt=batchadapt.batchadapt:main',],
    },
)
