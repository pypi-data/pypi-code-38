from setuptools import setup, find_packages

setup(
    name = 'cfn-dep2layer',
    version = '0.1.4',
    keywords = ('aws', 'lambda', 'layer', 'dependencies'),
    description = 'Package dependencies to layer',
    url = 'https://github.com/Just4test/aws-lambda-dependencies-to-layer',
    license = '',
    install_requires = ['cfn-yaml'],

    author = 'Just4test',
    author_email = 'myservice@just4test.net',
    
    scripts=['bin/dep2layer'],
    
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
    
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3 :: Only'
    ],
    
    packages = find_packages(),
    include_package_data=True,
    platforms = 'any'
)
