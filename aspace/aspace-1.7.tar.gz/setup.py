from setuptools import setup

setup(name='aspace',
	version='1.7',
	description='Client for working with REST API for ArchivesSpace',
	url='https://github.com/polkmetadatalib/aspace',
	author='Patrick Harrington',
	author_email='harringp@uwosh.edu',
	license='MIT',
	packages=['aspace'],
	install_requires=['requests'],
	python_requires='>=3',
	zip_safe=False)
	