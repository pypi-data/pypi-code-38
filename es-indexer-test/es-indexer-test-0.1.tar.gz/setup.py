from setuptools import setup

setup(
        author='Rounak Vyas',
        author_email='itsron143@gmail.com',
        name='es-indexer-test',
        version='0.1',
        description='A command line tool written in Python to help quickly populate json data into Elasticsearch.',
        url='https://github.com/itsron717/es-indexer-test',
        license='MIT',
        packages=['es_indexer_test'],
        install_requires=[
            'Click', 'elasticsearch',
            ],
        entry_points={
            'console_scripts': [
                'es-indexer-test=es_indexer_test:main',
                ]
            },
)