import setuptools

with open("README.md",'r') as fh:
	long_description = fh.read()

setuptools.setup(
	name = "LiDARtoolkit",
	version = "0.5",
	author = "Ekan5h",
	author_email = "ekanshmahendru@gmail.com",
	description = "A toolkit to handle LIDAR point cloud data.",
	long_description = long_description,
	long_description_content_type = "text/markdown",
	url = "https://github.com/Ekan5h/LIDARtoolkit",
	packages = setuptools.find_packages(),
	classifiers = [
		"Programming Language :: Python :: 3",
		"Operating System :: OS Independent"
	]
)

