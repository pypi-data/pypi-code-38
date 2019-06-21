from setuptools import setup

readme = open('README.rst').read()


install_requires=[
    'future',
    'gitpython',
    'jsonschema',
    'pyyaml>=5.1'
]


tests_require = [
    'coverage>=4.0',
    'coveralls',
    'nose'
]


extras_require = {
    'docs': [
        'Sphinx',
        'sphinx-rtd-theme'
    ],
    'tests': tests_require,
}


setup(
    name='benchmark-templates',
    version='0.1.1',
    description='Workflow Templates for Reproducible Data Analysis Benchmarks',
    long_description=readme,
    long_description_content_type='text/x-rst',
    keywords='reproducibility benchmarks data analysis',
    url='https://github.com/scailfin/benchmark-templates',
    author="Heiko Mueller",
    author_email="heiko.muller@gmail.com",
    license='MIT',
    packages=['benchtmpl'],
    include_package_data=True,
    test_suite='nose.collector',
    extras_require=extras_require,
    tests_require=tests_require,
    install_requires=install_requires
)
