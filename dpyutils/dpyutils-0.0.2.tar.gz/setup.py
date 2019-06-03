from setuptools import setup, find_packages

setup(
    name='dpyutils',
    version='0.0.2',
    description='A set of utilities for discord.py',
    url='https://github.com/KowlinMC/D.PY-utils',
    author='Kowlin',
    author_email='chromeuser1@outlook.com',
    license='MIT',
    python_requires='>=3.6',
    packages=find_packages(exclude=['tests', 'docs']),
    data_files=None
)