from setuptools import setup

setup(
        author='Rounak Vyas',
        author_email='itsron143@gmail.com',
        name='etesting-one',
        version='0.1',
        description='A command line tool written in Python to help quickly populate json data into Elasticsearch.',
        url='https://github.com/itsron717/etesting',
        license='MIT',
        packages=['elsi_testing_two'],
        install_requires=[
            'Click', 'elasticsearch',
            ],
        entry_points={
            'console_scripts': [
                'etesting-one=elsi_testing_two:main',
                ]
            },
)