import setuptools

with open('README.md', 'r') as fh:
	long_description = fh.read()

setuptools.setup(
	name='repltalk',
	version='0.6.0',
	author='mat',
	author_email='mat@matdoes.dev',
	description='Allows you to do various things with the slightly unofficial Repl Talk API',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://repl.it/talk',
	packages=setuptools.find_packages(),
	install_requires='aiohttp',
	classifiers=[
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
	],
)