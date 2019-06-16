from setuptools import setup

with open("README.md", 'r') as f:
	long_description = f.read()

setup(
	name='Mishap',
	version='0.1',
	license='MIT',
	description='For those times when your code is a bit too simple to understand',
	long_description=long_description,
	author='Param Thakkar',
	author_email='contact@param.me',
	packages=['mishap'],
)
