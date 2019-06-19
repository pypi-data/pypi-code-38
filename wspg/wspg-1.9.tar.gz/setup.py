from setuptools import setup

setup(
    name='wspg',
    version='1.9',

    description="Expose PostgreSQL databases via a websocket",
    url="https://bitbucket.org/gclinch/wspg",
    license='Apache License, Version 2.0',

    author='Graham Clinch',
    author_email='g.clinch@lancaster.ac.uk',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Database'
    ],

    packages=['wspg'],
    install_requires=[
        'aiopg', 'jquery-querybuilder-psycopg2', 'PyJWT',
        'psycopg2', 'websockets'
    ],
    entry_points={'console_scripts': [
        'wspg=wspg.application:run'
    ]})
