import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="AlfonsIoT",
	version="0.0.5.1",
	author="Anton Lindroth",
	author_email="ntoonio@gmail.com",
	description="A package for IoTs to interact with Alfons",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/ntoonio/AlfonsIoT.git",
	packages=setuptools.find_packages(),
	install_requires=[
		"pyyaml>=4.2b1",
		"paho-mqtt==1.3.1"
	]
)
