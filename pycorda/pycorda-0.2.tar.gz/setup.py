from setuptools import setup

setup(
	name='pycorda',
	version='0.2',
	author='Jamiel Sheikh',
	packages=['pycorda'],
	install_requires=[
		'jaydebeapi',
		'pandas',
		'requests'
	],
	include_package_data=True,
)