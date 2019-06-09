from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
        name='meander',
        version='0.0.3',
        description='Tools for computing contours on 2d surfaces.',
        long_description=readme(),
        url='https://github.com/austinschneider/meander',
        author='Austin Schneider',
        author_email='austin.schneider@icecube.wisc.edu',
        license='LGPL-3.0',
        packages=['meander'],
        zip_safe=False,
    )

