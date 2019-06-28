import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name = "mcautograder",
	version = "0.0.5",
	author = "Chris Pyles",
	author_email = "cpyles@berkeley.edu",
	description = "Small multiple choice question autograding library",
	long_description = long_description,
	long_description_content_type = "text/markdown",
	url = "https://github.com/chrispyles/mcautograder",
	packages = setuptools.find_packages(),
	classifiers = [
		"Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
	],
)