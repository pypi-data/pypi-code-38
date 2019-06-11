from setuptools import setup

setup(
        author='Rounak Vyas',
        author_email='itsron143@gmail.com',
        name='elsi-testing-one',
        version='0.1',
        description='A command line tool written in Python to help quickly populate json data into Elasticsearch.',
        url='https://github.com/itsron717/elsi-test-three',
        license='MIT',
        packages=['elsi_test_ing'],
        install_requires=[
            'Click', 'elasticsearch',
            ],
        entry_points={
            'console_scripts': [
                'elsi-testing-one=elsi_test_ing:main',
                ]
            },
)