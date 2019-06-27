from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    readme = f.read()

setup(
    name='evolvcli',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    license='Apache License 2.0',
    description='CLI user for creating and maintaining Evolv experiments.',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Frazer Bayley',
    author_email='frazer.bayley@evolv.ai',
    url='https://github.com/evolv-ai/experiment-management-cli',
    download_url='https://github.com/evolv-ai/experiment-management-cli/archive/1.0.0.tar.gz',
    keywords=['cli', 'Evolv', 'experiments', 'optimization'],
    install_requires=[
        'Click', 'requests'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.7',
    ],
    entry_points='''
        [console_scripts]
        evolv=evolvcli.cli:cli
    ''',
)
