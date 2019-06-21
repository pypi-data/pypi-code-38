from setuptools import setup

setup(name='crawler_core',
      version='1.10',
      description='Core programs for crawling',
      url='https://bitbucket.org/DraganMatesic/crawler_core',
      author='Dragan Matesic',
      author_email='dragan.matesic@gmail.com',
      license='MIT',
      packages=['core'],
      zip_safe=False,
      install_requires=['SQLAlchemy', 'pandas', 'requests', 'bs4', 'stem', 'pymssql', 'pyodbc', 'stem'],
      )
