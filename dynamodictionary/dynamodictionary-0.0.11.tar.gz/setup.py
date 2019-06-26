import setuptools

setuptools.setup(
    author_email='joseph.bylund@gmail.com',
    author='Joe Bylund',
    description='Dictionary like thing built on top of dynamodb',
    name='dynamodictionary',
    package_dir={'dynamodict': 'src/dynamodict'},
    packages=['dynamodict'],
    url="https://github.com/jbylund/dynamodictionary",
    version='0.0.11',
)
