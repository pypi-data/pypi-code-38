from distutils.core import setup
setup(
  name = 'tetumnlp',        
  packages = ['tetumnlp'],  
  version = '0.1.1',      
  license='GNU',        
  description = 'Tetum tokenizer and translater',   
  author = 'Maun Rhys',                  
  author_email = 'maun.rhys@gmail.com',      
  url = 'https://github.com/maunrhys/tetumnlp',  
  download_url = 'https://github.com/maunrhys/tetumnlp/archive/v0.1.1.tar.gz',  
  include_package_data = True,  
  keywords = ['NLP', 'MINORITY LANGUAGE'],  
  install_requires=[           
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',      
    'Topic :: Text Processing :: Linguistic',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)', 
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',

  ],
)