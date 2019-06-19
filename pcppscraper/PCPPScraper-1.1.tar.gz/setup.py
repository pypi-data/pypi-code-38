from setuptools import setup

setup(name='PCPPScraper',
      version='1.1',
      description='A simple scraper for PCPP Lists',
      url='https://github.com/A1phyte/PCPPScraper',
      author='Bryan Li',
      author_email='bryanyuezhouli@gmail.com',
      license='MIT',
      packages=['PCPPScraper'],
      install_requires=[
          'requests',
          'beautifulsoup4'
      ],
      zip_safe=False)