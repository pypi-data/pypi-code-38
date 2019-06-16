from setuptools import setup

with open("README.md", 'r') as f:
	long_description = f.read()

setup(
	name='Mishap',
	version='0.2',
	license='MIT',
	url = 'http://github.com/paramt/mishap',
	description='For those times when your code is a bit too simple to understand',
	long_description=long_description,
	long_description_content_type='text/markdown',
	author='Param Thakkar',
	author_email='contact@param.me',
	packages=['mishap'],
	classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
		'Intended Audience :: Developers',
    ],
)
