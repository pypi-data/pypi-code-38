
from setuptools import setup

setup(
	name='python-simple-html-sanitize',
	version='0.0.1',
	description='Only keep the text and bold, italic, underline and new line tags into an html string',
	packages=['simple_html_sanitizer'],
	url='https://github.com/remaudcorentin-dev/python-simple-html-sanitize',
	author='Corentin Remaud',
	author_email='remaudcorentin.dev@gmail.com',
	license='MIT',
	zip_safe=False,
	install_requires=['bs4'],
	)
