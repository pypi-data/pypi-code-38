from setuptools import setup


setup(
	name='chromedriver_install',
	version='1.0.3',
	description='Package for installing the latest chrome/firefox webdrivers automatically.',
	long_description="This package has changed names, please use the new version, https://pypi.org/project/pyderman/ instead.",
	url='http://github.com/shadowmoose/chrome_driver',
	author='ShadowMoose',
	author_email='shadowmoose@github.com',
	license='MIT',
	packages=['pyderman'],
	install_requires=[],
	zip_safe=False)

# python setup.py sdist;twine upload dist/*
