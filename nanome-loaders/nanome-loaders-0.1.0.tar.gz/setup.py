import pathlib
from setuptools import find_packages, setup

README = (pathlib.Path(__file__).parent / "README.md").read_text()

setup(
	name = 'nanome-loaders',
	packages=find_packages(),
	version = '0.1.0',
	license='MIT',
	description = 'Nanome Plugin deploying a few molecle loaders integrated with Nanome',
	long_description = README,
    long_description_content_type = "text/markdown",
	author = 'Nanome',
	author_email = 'hello@nanome.ai',
	url = 'https://github.com/nanome-ai/plugin-loaders',
	platforms="any",
	keywords = ['virtual-reality', 'chemistry', 'python', 'api', 'plugin'],
	install_requires=['nanome'],
	entry_points={"console_scripts": ["nanome-url-loader = nanome_loaders.URLLoader:main", "nanome-web-loader = nanome_loaders.WebLoader:main"]},
	classifiers=[
		'Development Status :: 3 - Alpha',

		'Intended Audience :: Science/Research',
		'Topic :: Scientific/Engineering :: Chemistry',

		'License :: OSI Approved :: MIT License',

		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
	],
	package_data={
        "nanome_loaders": [
            "_WebLoader/*",
        ]
	},
)