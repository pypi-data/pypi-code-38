import setuptools

with open('README.md', 'r') as f:
	readme = f.read()

packages = setuptools.find_packages(include=['userutils'], exclude=['userutils.examples', ])
print('Found the following packages: ', "\n".join(packages), sep='\n')

setuptools.setup(name='userutils',
	version='2.0.0',
	description='Makes working with humans easier',
	long_description=readme,
	long_description_content_type='text/markdown',
	url='https://github.com/Scoder12/userutils',
	author='Scoder12',
	author_email='realscoder12@gmail.com',
	license='MIT',
	packages=packages,
	classifiers=[
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
	],
)
