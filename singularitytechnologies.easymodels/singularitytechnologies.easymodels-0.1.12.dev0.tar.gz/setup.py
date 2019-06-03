import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='singularitytechnologies.easymodels',
    version='0.1.12dev',
    author='Sam Lacey',
    author_email='sam.lacey@singularity-technologies.io',
    description='Easy to use Machine Learning training classes',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/singularitydigitaltechnologies/easymodels',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
)
