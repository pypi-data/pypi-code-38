from setuptools import setup, find_packages

setup(
    name='evolvclient',
    version='0.1',
    author='Evolv.ai',
    packages=find_packages(),
    install_requires=[
        'requests==2.21.0'
    ],
    description='Evolv Experiment SDK for Python'
)
