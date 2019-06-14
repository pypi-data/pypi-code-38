from setuptools import setup

setup(name='feebee',
      version='0.5.31',
      description='datawork tools',
      url='https://github.com/nalssee/feebee.git',
      author='nalssee',
      author_email='kenjin@sdf.org',
      license='MIT',
      packages=['feebee'],
      # Install statsmodels manually using conda install
      # TODO: Not easy to install numpy and stuff without conda
      install_requires=[
          'openpyxl>=2.5.12',
          'sas7bdat>=2.0.7',
          'psutil>=5.4.3',
          'graphviz>=0.8.2',
          'pathos>=0.2.2.1',
          'xlrd>=0.9.0',
          'more-itertools>=5.0.0',
          'coloredlogs>=10.0',
          'tqdm>=4.29.1',
          # requires c/c++ compiler installation
          'ciso8601>=2.1.1',
          'pandas',
        ],
      zip_safe=False)
