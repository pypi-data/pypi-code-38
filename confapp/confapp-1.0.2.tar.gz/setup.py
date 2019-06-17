import os, re; from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme: README = readme.read()
with open(os.path.join(os.path.dirname(__file__), 'confapp','__init__.py')) as fd:
	__version__ = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)

setup(
	name='confapp',
	version=__version__,
	packages=find_packages(),
	include_package_data=True,
	description='Python library that implements a singleton object to use as settings system.',
	url='https://github.com/UmSenhorQualquer/confapp',
	author='Ricardo Jorge Vieira Ribeiro',
	author_email='ricardojvr@gmail.com',
	classifiers=[
		'Intended Audience :: Developers',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
	],
)