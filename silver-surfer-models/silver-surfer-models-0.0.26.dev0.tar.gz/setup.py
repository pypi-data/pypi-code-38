import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()


INSTALL_REQUIRES = [
    'marshmallow==2.10.5',
    'PyMySQL==0.9.3',
    'python-dateutil==2.8.0',
    'pytz==2019.1',
    'SQLAlchemy==1.2.15',
    'boto3==1.9.134',
    'botocore==1.12.134',
    's3transfer==0.2.0',
    'six==1.12.0',
    'urllib3==1.24.2',
    'dnspython==1.16.0',
    'pymongo==3.8.0',
]

if __name__ == '__main__':
    setuptools.setup(
        name='silver-surfer-models',
        version='0.0.26-dev',
        author='Harsh Verma',
        author_email='harsh376@gmail.com',
        description='MySQL db models',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/harsh376/silver-surfer-models',
        packages=setuptools.find_packages(where='src'),
        package_dir={'': 'src'},
        classifiers=[
            'Programming Language :: Python :: 3',
        ],
        install_requires=INSTALL_REQUIRES,
        python_requires='~=3.6',
    )
