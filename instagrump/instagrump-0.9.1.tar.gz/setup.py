import os
from setuptools import setup

def read(fname):
		return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
		name = 'instagrump',
		packages = ['instagrump'],
		version = '0.9.1',
		license='MIT',
		description = 'Instagram public API wrapper',
		install_requires = ['requests'],
		author = 'Kelvin Ananda',
		author_email = 'ananda.kelvin@gmail.com',
		url = 'https://github.com/anandakelvin/instagrump', 
		keywords = ['Instagram', 'wrapper', 'public','API'],
		long_description=read('README.md'),
		long_description_content_type='text/markdown',
		classifiers=[
				"Development Status :: 4 - Beta",
				"Topic :: Utilities",
				"License :: OSI Approved :: MIT License",
		],
)