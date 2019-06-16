from setuptools import setup

import roboversion as package


details = {
	'name': package.__name__,
	'description': 'Automated project versioning using Git repository state',
	'long_description': package.__doc__,
	'version': str(package.get_version()),
	'author': 'David Finn',
	'author_email': 'dsfinn@gmail.com',
	'url': 'https://github.com/dsfinn/roboversion.git',
	'packages': [package.__package__],
	'python_requires': '>=3.6',
	'classifiers': [
		'Programming Language :: Python :: 3.6',
		(
			'License :: OSI Approved'
			' :: GNU General Public License v3 or later (GPLv3+)'
		),
		'Operating System :: OS Independent',
		'Intended Audience :: Developers',
		'Topic :: Software Development :: Version Control',
		'Topic :: Software Development :: Version Control :: Git',
		'Topic :: Utilities',
	],
}


if __name__ == '__main__':
	setup(**details)
