from setuptools import setup

with open("README.md", "r") as fh:
	long_desc = fh.read()

setup(
	name = 'komodorpc',
	#packages = ['komodorpc'], # this must be the same as the name above
	version = '1.0',
	description = 'RPC API-Library for Komodo-based asset chains, for Python DApp Developers',
	long_description = long_desc,
	long_description_content_type = "text/markdown",
	author = 'Vaibhav Murkute',
	author_email = 'vaibhavmurkute88@gmail.com',
	license='MIT',
	package_dir={'':'src'},
	py_modules=["komodo_rpc", "rpc_util.rpc", "komodo.address", "komodo.blockchain", "komodo.control", "komodo.disclosure", "komodo.generate", "komodo.jumblr", "komodo.mining", "komodo.network", "komodo.raw_transactions", "komodo.util", "komodo.wallet"],
	install_requires=[
			'requests>=2.22.0'
	],
	url = 'https://github.com/V413H4V/Komodo-RPC-Library-Python/', # use the URL to the github repo
	#download_url = 'https://github.com/peterldowns/mypackage/archive/0.1.tar.gz', # I'll explain this in a second
	keywords = ['komodorpc', 'komodo'], # arbitrary keywords
	classifiers = [
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
	],
)