import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="file-tools",
	version="0.1.6",
	author="Edmund Pfeil",
	author_email="edmundpf@buffalo.edu",
	description="File and JSON File Methods.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/edmundpf/file_tools",
	install_requires=[],
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
)
