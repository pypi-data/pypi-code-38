from setuptools import setup


setup(
    name='demyst-cli',

    version='0.7.34',

    description='',
    long_description='',

    author='Demyst Data',
    author_email='info@demystdata.com',

    license='',
    entry_points='''
        [console_scripts]
        demyst=demyst.cli.command:cli
    ''',
    packages=['demyst.cli'],
    include_package_data=True,
    zip_safe=False,

    install_requires=[
        'demyst-common>=0.7.34',
        'click',
        'boto3',
        'botocore',
        'tabulate',
        'halo',
        'glom'
    ]
)
