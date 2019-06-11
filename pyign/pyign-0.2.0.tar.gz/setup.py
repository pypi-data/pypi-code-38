from setuptools import setup, find_packages

def readme():
    with open('README.md','r') as f:
        return f.read()

#needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
#pytest_runner = ['pytest-runner'] if needs_pytest else []

setup(
    name = 'pyign',
    version = '0.2.0',

    description = 'A python package used to monitor sensors and control a liquid rocket engine test stand system',
    long_description = readme(),

    classifiers = [
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
    ],
    url = 'https://github.com/devonburson/PyIGN',

    author = 'Devon Burson',
    author_email = 'bursond@oregonstate.edu',
    license = 'MIT',

    install_requires = [
        'markdown',
        'numpy',
    ],

    #tests_require = [
    #    'pytest',
    #    'pytest-cov',
    #],

    #tests_require = tests_require,
    #setup_requires = setup_requires,

    include_package_data = True,
    packages = find_packages(),
    zip_safe = False,
    )
