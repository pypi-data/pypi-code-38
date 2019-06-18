from setuptools import setup, find_packages

setup(
    name='demojd',
    description='Hello World demo with tree package structure.',
    author='vipervit',
    author_email='vitolg1@gmail.com',
    version='0.38',
    long_description=open('README.rst').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    package_data={'': ['*.json']},
    scripts=['demojd/scripts/hello.py']
)
