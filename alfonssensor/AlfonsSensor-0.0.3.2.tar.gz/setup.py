import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
	install_requires = fh.read().splitlines()

setuptools.setup(
    name="AlfonsSensor",
    version="0.0.3.2",
    author="Anton Lindroth",
    author_email="ntoonio@gmail.com",
    description="A package for sensors to interact with Alfons",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ntoonio/AlfonsSensor.git",
    packages=setuptools.find_packages(),
	install_requires=install_requires,
	entry_points = {
		"console_scripts": [
			"alfons_sensor = AlfonsSensor.__main__:main",
		],
	}
)
