from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='db_access',
      version='0.1.2',
      description='Easy db access through sqlalchemy',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Weiyi Yin',
      url='https://github.com/weiyiyin0321/easy_db_access.git',
      packages=['db_access'],
      install_requires=[
          'cx_Oracle',
          'pyodbc',
          'sqlalchemy',
          'impyla',
          'pymysql'
      ],
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      zip_safe=False)
