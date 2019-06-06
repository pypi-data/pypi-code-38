from distutils.core import setup
setup(
  name = 'biasMetrics',      
  packages = ['biasMetrics'],
  version = '0.4.0',      
  license='MIT',        
  description = 'Set of classification metrics to determine bias in underrepresented subpopulations.',  
  author = 'Brandon Walraven',
  author_email = '',      
  url = 'https://github.com/bcwalraven',
  download_url = 'https://github.com/bcwalraven/biasMetrics/archive/v0.4.0.tar.gz',    
  keywords = ['AUC', 'Classification', 'Metrics'],   
  install_requires=[           
          'numpy',
          'pandas',
          'seaborn',
          'sklearn',
          'scipy'
      ],
)