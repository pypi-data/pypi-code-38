from distutils.core import setup

setup(
	name='listorm',
	version='0.2.14',
	description='SQL ORM API for table type of dict-list',
	author = 'HS Moon',
	author_email = 'mhs9089@gmail.com',
	py_modules = ['listorm'],
	install_requires=['xlrd', 'xlsxwriter'],
	url='https://github.com/zwolf21/listorm'
)
