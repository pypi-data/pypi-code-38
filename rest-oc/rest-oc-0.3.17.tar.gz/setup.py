from setuptools import setup

setup(
	name='rest-oc',
	version='0.3.17',
	url='https://github.com/ouroboroscoding/rest-oc-python',
	description='RestOC is a library of python 3 modules for rapidly setting up REST microservices.',
	keywords=['rest','microservices'],
	author='Chris Nasr - OuroborosCoding',
	author_email='ouroboroscode@gmail.com',
	license='Apache-2.0',
	packages=['RestOC'],
	install_requires=[
		'bottle==0.12.13',
		'format-oc==1.5.5',
		'gunicorn==19.9.0',
		'hiredis==0.2.0',
		'Jinja2==2.10',
		'pdfkit==0.6.1',
		'Pillow==5.3.0',
		'redis==2.10.6',
		'requests==2.20.1',
		'rethinkdb==2.4.1'
	],
	zip_safe=True
)
