import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

with open("requirements.txt", "r") as fh:
	install_requires = fh.read().splitlines()

setuptools.setup(
	name="AlfonsIoT",
	version="0.0.5",
	author="Anton Lindroth",
	author_email="ntoonio@gmail.com",
	description="A package for IoTs to interact with Alfons",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/ntoonio/AlfonsIoT.git",
	packages=setuptools.find_packages(),
	install_requires=install_requires
)
