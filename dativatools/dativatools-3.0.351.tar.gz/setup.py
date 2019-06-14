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
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'Topic :: Software Development :: Libraries',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3.6'],
      keywords='dativa',)
