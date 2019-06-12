from setuptools import setup

setup(
        author='Rounak Vyas',
        author_email='itsron143@gmail.com',
        name='etesting',
        version='0.1',
        description='A command line tool written in Python to help quickly populate json data into Elasticsearch.',
        url='https://github.com/itsron717/etesting',
        license='MIT',
        packages=['elsi_testing_one'],
        install_requires=[
            'Click', 'elasticsearch',
            ],
        entry_points={
            'console_scripts': [
                'etesting=elsi_testing_one:main',
                ]
            },
)