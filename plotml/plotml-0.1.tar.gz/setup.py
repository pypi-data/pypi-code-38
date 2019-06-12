from distutils.core import setup
setup(
  name = 'plotml',
  packages = ['plotml'],
  version = '0.1',
  license='MIT',
  description = 'Some neat plotting functions for ML',
  author = 'Patrick Schrempf',
  author_email = 'pschrempf@outlook.com',
  url = 'https://github.com/pschrempf/plotml',
  download_url = 'https://github.com/pschrempf/plotml/archive/0.1.tar.gz',  
  keywords = ['plot', 'machine-learning'],
  install_requires=[           
          'numpy',
          'matplotlib',
          'itertools',
  ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
  ],
)
