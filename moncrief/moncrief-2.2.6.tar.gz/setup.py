import setuptools

setuptools.setup(
    name='moncrief',
    version='2.2.6',
    url='https://github.com/AlgernonSolutions/algernon',
    license='GNU Affero General Public License v3.0',
    author='algernon_solutions/jcubeta',
    author_email='jcubeta@algernon.solutions',
    description='This library contains the basic units of functionality and infrastructure needed to effectively run '
                'operations and applications in a distributed and severless fashion.',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'aws-xray-sdk',
        'boto3',
        'botocore',
        'certifi',
        'chardet',
        'docutils',
        'future',
        'idna',
        'jmespath',
        'jsonpickle',
        'jsonref',
        'python-dateutil',
        'python-rapidjson',
        'pytz',
        'requests',
        's3transfer',
        'six',
        'urllib3',
        'wrapt'
    ],
)
