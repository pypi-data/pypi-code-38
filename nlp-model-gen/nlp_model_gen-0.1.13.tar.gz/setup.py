# @Vendors
import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='nlp_model_gen',
    version='0.1.13',
    author='Gerardo Alias',
    author_email='alias_gerardo@yahoo.com.ar',
    description='A spaCy model customizer and management tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,
    url='https://github.com/galias11/nlp_model_gen',
    packages=setuptools.find_packages(),
    scripts=['scripts/nlp_model_gen_install.sh'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'spacy ==2.0.18 ',
        'pymongo >=3.7.2',
        'schema >=0.6.8',
        'termcolor >=1.1.0',
        'terminaltables >=3.1.0',
        'gitpython >=2.1.11'
    ]
)