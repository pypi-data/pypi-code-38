

from setuptools import setup, find_packages

print(find_packages())

setup(name='VisualGraphDebugger-zacharyh211',
	version='0.6',
	description='GUI debugger and graph library for writing and debugging graph algorithms',
	author='Zachary Hancock',
	packages=['graphdebugger'],
	package_dir={'graphdebugger':'graphdebugger'},
	package_data={
		'graphdebugger': [
			'assets/*',
			'graphs/*',
			'samples/*',
		]	
	},
	install_requires=['PyQt5'],
	entry_points={
		'gui_scripts': ['vgd = graphdebugger.run:main']
	},
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
	],
)

