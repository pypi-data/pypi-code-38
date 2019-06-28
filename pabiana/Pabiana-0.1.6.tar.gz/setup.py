from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

setup(
	name='Pabiana',
	version=open(path.join(here, 'VERSION.txt')).read().strip(),
	packages=find_packages(),
	install_requires=open(path.join(here, 'requirements.txt')).read().split('\n'),
	setup_requires=['pytest-runner >= 4.4'],
	tests_require=['pytest >= 4.4.1'],
	zip_safe=False,
	
	url='https://github.com/kankiri/pabiana',
	author='Alexander Schöberl',
	author_email='alexander.schoeberl@gmail.com',
	description='A minimalistic framework to build distributed cognitive applications based on ØMQ',
	long_description=open(path.join(here, 'README.md')).read(),
	long_description_content_type='text/markdown',
	keywords=['framework', 'cognitive', 'distributed', 'ØMQ'],
	license='MIT'
)
