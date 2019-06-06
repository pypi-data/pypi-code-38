from setuptools import setup

setup(name='social_scrape',
      version='0.2',
      description='Scrapes social platforms using bs4',
      url='https://github.com/ghandic/social_scrape',
      author='Andy Challis',
      author_email='andrewchallis@hotmail.co.uk',
      install_requires=['requests', 'bs4'],
      packages=['social_scrape'],
      zip_safe=False,
      include_package_data=True,
      python_requires=">=3.6",
      entry_points={
          'console_scripts': 'social_scrape=social_scrape.cli:main'
      })
