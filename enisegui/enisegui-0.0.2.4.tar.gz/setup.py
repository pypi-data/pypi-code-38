#import setuptools
from distutils.core import setup
setup(
      name = 'enisegui',
      packages = ['enisegui'],
      package_data = {'enisegui':['*.txt','*.png']},                    
      version = '0.0.2.4',
      description = 'Widgets for guizero',
      author = 'BagEddy42',
      author_email = 'edouard.vidal@enise.fr',
      keywords = ['gui', 'guizero'], # arbitrary keywords
      install_requires=[
          'guizero',
      ],
      classifiers = [],
)
