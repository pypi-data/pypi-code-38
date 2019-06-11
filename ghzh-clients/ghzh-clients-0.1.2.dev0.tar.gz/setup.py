from setuptools import find_packages, setup

requires = ['github3.py', 'backoff', 'requests']

setup(
    name='ghzh-clients',
    version='0.1.2.dev0',
    description='A library that combines GitHub and ZenHub '
                'clients used for various OpenStax reports',
    long_description='',
    url='https://github.com/openstax/ghzh-clients',
    license='AGPLv3',
    author='m1yag1',
    author_email='qa@openstax.org',
    packages=find_packages(),
    install_requires=requires,
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-vcr', 'pytest-cov'],
    zip_safe=False,
    classifiers=[],
)
