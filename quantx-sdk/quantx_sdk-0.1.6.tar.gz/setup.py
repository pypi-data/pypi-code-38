from setuptools import setup, find_packages

requires = [
    "requests>=2.19.1",
    "pandas>=0.23.4",
    "websocket-client>=0.51.0",
    "Jinja2>=2.10.1"
]
version = open('VERSION').read().strip()
setup(
    name='quantx_sdk',
    version=version,
    author='Smart Trade Inc.',
    author_email='dev@smarttrade.co.jp',
    url='https://factory.quantx.io/',
    description='QuantX SDK',
    long_description=open('README.md').read().strip(),
    long_description_content_type="text/markdown",
    license='Apache License Version 2.0',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=requires,
)
