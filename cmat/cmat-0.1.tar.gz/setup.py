from distutils.core import setup 

setup(
  name = 'cmat',
  packages = [ 'cmat' ],
  version = 0.1,
  license = 'MIT',
  description = 'Utility package for creating, analyzing, and plotting confusion matrices',
  author = 'sherilan',
  author_email = 'sherilan@protonmail.com',
  url = 'https://github.com/sherilan/cmat',
  # download_url = ,
  keywords = [ 'confusion matrix', 'data science', 'machine learning' ],
  install_requires = [
    'pandas',
    'numpy'
  ],
  classifiers = [
    'Development Status :: 3 - Alpha',
    'Operating System :: OS Independent',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Topic :: Scientific/Engineering',
  ]
)