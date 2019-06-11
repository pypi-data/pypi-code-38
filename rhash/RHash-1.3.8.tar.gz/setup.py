from setuptools import setup, Distribution
from wheel.bdist_wheel import bdist_wheel

class BinaryDistribution(Distribution):
	def has_ext_modules(foo):
		return True

class my_bdist_wheel(bdist_wheel):
	def get_tag(self):
		python, abi, plat = bdist_wheel.get_tag(self)
		return "py2.py3", "none", plat

with open("README.md", "r", encoding="utf-8") as fr:
	long_description = fr.read()

setup(
	name="RHash",
	version="1.3.8",
	url="https://github.com/rhash/RHash",
	maintainer="Dobatymo",
	description="Windows binary wheels for RHash",
	long_description=long_description,
	long_description_content_type="text/markdown",
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"Intended Audience :: Science/Research",
		"Operating System :: Microsoft :: Windows",
		"Programming Language :: Python :: 2",
		"Programming Language :: Python :: 3",
		"Topic :: Internet",
		"Topic :: Scientific/Engineering",
		"Topic :: Utilities"
	],

	py_modules=["rhash"],
	data_files=["librhash.dll"],
	distclass=BinaryDistribution,
	cmdclass={"bdist_wheel": my_bdist_wheel}
)
