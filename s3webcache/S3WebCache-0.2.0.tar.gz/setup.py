import setuptools

setuptools.setup(
    name='S3WebCache',
    version='0.2.0',
    packages=setuptools.find_packages(),
    license='MIT',
    author_email="dhking@wharton.upenn.edu",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=["requests",
                      "boto3"],
    test_suite='nose.collector',
    tests_require=['nose'],
)
