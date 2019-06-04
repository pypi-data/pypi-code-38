from setuptools import setup

with open('README.md') as f:
    long_description = f.read()


def get_version():
    return open('version.txt', 'r').read().strip()

setup(name='dativatools',
      version=get_version(),
      description='A selection of tools for easier processing of data using Pandas and AWS',
      long_description=long_description,
      # long_description='Project Repositry: https://bitbucket.org/dativa4data/dativatools/',
      long_description_content_type="text/markdown",
      url='https://bitbucket.org/dativa4data/dativatools/',
      author='Dativa',
      author_email='hello@dativa.com',
      license='MIT',
      zip_safe=False,
      packages=['dativatools',
                'dativa.tools',
                'dativa.tools.pandas',
                'dativa.tools.aws',
                'dativa.tools.logging',
                'dativa.tools.db'],
      include_package_data=True,
      setup_requires=[
          'setuptools>=41.0.1',
          'wheel>=0.33.4'],
      install_requires=[
          'awsretry>=1.0.1',
          'boto3>=1.4.4',
          'chardet>=3.0.4',

          # Note pandas is hard coded to a specific version
          'pandas==0.23.4',
          #
          # The function string_to_datetime in dativa/tools/pandas/datetime.py is deeply
          # linked to internal pandas calls as it provides a sensible implementation of
          # pd.to_datetime that does not automatically convert all ISO8601 format strings
          # regardless of format.
          #
          # if you want to upgrade to a new version of Pandas then you need to update this code
          # to match the version you want

          'paramiko>=2.2.3',
          'patool>=1.12',
           # Version 2.8 of psycopg2 caused a lot of issues, it doesn't even pip install properly.
          'psycopg2==2.7.7',
          'pexpect>=4.2.1',
          's3fs>=0.1.5',
          'pyarrow==0.10.0',
          'requests>=2.19.0',
          'blist>=1.3.6',
          'pycryptodome>=3.7.2'
      ],
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'Topic :: Software Development :: Libraries',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3.6'],
      keywords='dativa',)
