from setuptools import setup
from io import open

setup(
    name='function-shield',
    zip_safe=True,
    version='2.0.0',
    long_description=open('README.rst', encoding="utf-8").read(),
    author='PureSec',
    author_email='support@puresec.io',
    packages=['function_shield'],
    url='https://github.com/puresec/FunctionShield',
    include_package_data=True
)
