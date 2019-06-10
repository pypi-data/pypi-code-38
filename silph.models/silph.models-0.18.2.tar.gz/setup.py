from setuptools import setup

lib_name = 'silph.models'

setup(
    name=lib_name,
    version='0.18.2',
    author='Marco Ceppi',
    author_email='marco@thesilphroad.com',
    description='Database models for TSR',
    license='other',
    classifiers=[
        'License :: Other/Proprietary License',
        'Topic :: Database',
        'Development Status :: 5 - Production/Stable',
    ],
    namespace_packages=['silph'],
    packages=[lib_name, 'silph.ext'],
    install_requires=[
        'asyncqlio==0.1.1.dev119',
        'aiomysql==0.0.19',
    ],
    dependency_links=[
        'git+https://github.com/Unplottable/asyncqlio.git@discord-bot#egg=asyncqlio-0.1.1.dev119',
        'git+https://github.com/aio-libs/aiomysql.git#egg=aiomysql',
    ]
)
