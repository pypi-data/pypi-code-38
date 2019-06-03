# -*- coding: utf-8 -*-

from setuptools import setup

setup(
	name='guid',
	packages=['guid'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[],
	#entry_points={
	#	'console_scripts': [
	#		'bake = bake.bake:main',
	#	]
	#},
	keywords='guid uuid python',
	version='0.1.0',
	description="Human friendly GUID/UUID library",
	long_description="Human friendly GUID/UUID library",
	author='Logi Leifsson',
	author_email='logileifs@gmail.com',
	url='https://github.com/logileifs/guid.git',
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
)
