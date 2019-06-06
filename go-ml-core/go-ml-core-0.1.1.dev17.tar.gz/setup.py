from setuptools import setup, find_packages

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
        name='go-ml-core',
        version='0.1.1.dev17',
	  	description='machine learning core library',
        long_description=long_description,
        long_description_content_type='text/markdown',
	  	packages=find_packages(exclude=['tests']),
		url='http://10.0.1.31/ML/ml-storage/ml-etl/',
		author='henrychi',
		author_email='shyuusaku@gmail.com',
		license='Gogoro Inc.',
		keywords='machine learning',
        classifiers = [
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Build Tools',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
        ],
		install_requires=[
			'boto3>=1.9.57',
			'pymongo>=3.7.2',
            'PyYAML>=3.13',
            'requests>=2.20.1'
		]
)
