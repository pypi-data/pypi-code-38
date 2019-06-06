import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="print-tools",
	version="0.0.5",
	author="Edmund Pfeil",
	author_email="edmundpf@buffalo.edu",
	description="Print styling/formatting methods.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/edmundpf/print_tools",
	install_requires=['colorful'],
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
)
