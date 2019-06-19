import setuptools


install_requirements = [
    'requests>=2.21.0,<2.22.0',
]

test_requires = ['pytest', 'pytest-vcr', 'pycodestyle', 'pytest-cov']

with open('README.md', 'r') as f:
    long_description = f.read()


setuptools.setup(
    name='stp_scraper',
    version='0.1.2',
    author='Cuenca',
    author_email='dev@cuenca.com',
    description='Extract sent and received transactions of an STP account.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/cuenca-mx/stp-scraper',
    packages=setuptools.find_packages(),
    install_requires=install_requirements,
    setup_requires=['pytest-runner'],
    tests_require=test_requires,
    extras_require=dict(test=test_requires),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)
