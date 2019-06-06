import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="datatype-tools",
	version="0.1.2",
	author="Edmund Pfeil",
	author_email="edmundpf@buffalo.edu",
	description="Additional methods for Python's immutable data types.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/edmundpf/datatype_tools",
	install_requires=['forbiddenfruit'],
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
)
