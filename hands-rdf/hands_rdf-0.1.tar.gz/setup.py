from setuptools import setup

setup(name='hands_rdf',
      version='0.1',
      description='Hand detector in depth images',
      url='',
      author="Bernat Galmés Rubert, Dr. Gabriel Moyà Alcover",
      author_email='bernat_galmes@hotmail.com',
      license='GPL',
      packages=['hands_rdf', 'hands_rdf.Model'],
      install_requires=[
          'scikit-learn',
          'numpy',
      ],
      zip_safe=False)
