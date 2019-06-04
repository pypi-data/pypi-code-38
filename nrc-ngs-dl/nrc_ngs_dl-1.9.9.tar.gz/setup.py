from setuptools import setup, find_packages
import os.path

readme_file = 'README.md'
readme = 'Cannot find the file:'+readme_file
if os.path.exists(readme_file):

    with open(readme_file) as f:

        readme = f.read()

requires_file = 'requirements.txt'
requires = 'Cannot find the file:'+requires_file
if os.path.exists(requires_file):

    with open(requires_file) as f:

        requires = f.read()

setup(

    name='nrc_ngs_dl',
    version='v1.9.9',
    description='software for downloading and handling sequence data from NRC-LIMS website',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Abbey Laoye',
    author_email='abiodun.laoye@canada.ca',
    license='MIT License',
    packages = find_packages(exclude=('test')),
    install_requires = requires,
    scripts = ['config.ini.sample'],
    entry_points={

        'console_scripts': [

            'lims_downloader = nrc_ngs_dl.lims_downloader:main',

            ],

    }

)


