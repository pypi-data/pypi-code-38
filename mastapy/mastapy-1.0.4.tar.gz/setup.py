import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="mastapy",
	version="1.0.4",
	author="Connor Thornley",
	author_email="connor.thornley@smartmt.com",
	description="A package for integrating scripts with Masta",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://www.smartmt.com/cae-software/masta/overview/",
	packages=setuptools.find_packages(),
	install_requires=[
		'pythonnet>=2.4.0',
	],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent"
	]
)