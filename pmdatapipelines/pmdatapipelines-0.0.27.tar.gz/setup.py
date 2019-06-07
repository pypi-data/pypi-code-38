import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="pmdatapipelines",
	version="0.0.27",
	author="Jørgen Frøland",
	author_email="jorgen.froland@polarismedia.no",
	description="Data pipeline library for Polaris Media",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="",
	packages=setuptools.find_packages(),
	install_requires=[
		'boto3',
		'pandas',
		'pyarrow',
	],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
)