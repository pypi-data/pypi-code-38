"""Setup flask-eztest."""

from setuptools import setup

requirements = [
    'Flask',
    'capybara-py',
    'selenium',
    'Flask-SQLAlchemy',
    'termcolor'
]

description = "Tool to make integration testing flask app's using flask_sqlalchemy package easy to set up and organized"

long_description = open('README.rst').read()

setup(
    name='flaskeztest3',
    version='0.3.4',
    author='Stanley Rokita',
    author_email='srok35@gmail.com',
    url='https://github.com/cmorterud/flask-eztest',
    description=description,
    long_description=long_description,
    install_requires=requirements,
    packages=['flaskeztest3'],
    entry_points={
        'console_scripts': [
            'eztest = flaskeztest3.__main__:flaskeztest_main'
        ]
    }
)
