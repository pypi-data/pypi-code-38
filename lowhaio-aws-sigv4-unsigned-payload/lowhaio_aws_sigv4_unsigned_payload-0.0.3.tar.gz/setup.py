import setuptools


def long_description():
    with open('README.md', 'r') as file:
        return file.read()


setuptools.setup(
    name='lowhaio_aws_sigv4_unsigned_payload',
    version='0.0.3',
    author='Michal Charemza',
    author_email='michal@charemza.name',
    description='AWS Signature Version 4 signing for lowhaio, but with UNSIGNED-PAYLOAD',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/michalc/lowhaio-aws-sigv4',
    py_modules=[
        'lowhaio_aws_sigv4_unsigned_payload',
    ],
    python_requires='>=3.6.0',
    test_suite='test',
    tests_require=[
        'lowhaio~=0.0.61',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: AsyncIO',
    ],
)
