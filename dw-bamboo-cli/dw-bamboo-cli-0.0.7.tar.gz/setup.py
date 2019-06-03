import setuptools

setuptools.setup(
    name='dw-bamboo-cli',
    packages=['bamboo_cli'],
    version='0.0.7',
    description='Command line interface for running Bamboo data pipelines',
    author='Jon Speiser',
    license='All Rights Reserved',
    install_requires=[
        'click',
        'bamboo-lib'
    ],
    entry_points={
        'console_scripts': [
            'bamboo-cli=bamboo_cli.main:runner',
        ],
    },
)
