"""
Flask-Lin
------------------
"""
from setuptools import setup

setup(name='Lin-CMS',
      version="0.1.1-beta3",
      url='https://gitee.com/gaopedro/Alkaid/tree/master',
      license='MIT',
      author='pedroGao',
      author_email='1312342604@qq.com',
      maintainer='pedroGao',
      maintainer_email='1312342604@qq.com',
      description='A CMS of Flask',
      long_description='一个 Python 🤷 版的 CMS 🔥',
      long_description_content_type="text/markdown",
      keywords=['flask', 'CMS', 'authority', 'jwt'],
      packages=['lin'],
      zip_safe=False,
      platforms='any',
      install_requires=[
          'WTForms==2.2.1',
          'Werkzeug==0.14.1',
          'Flask==1.0.2',
          'SQLAlchemy==1.2.11',
          'Flask_JWT_Extended==3.12.1',
          'Flask_SQLAlchemy==2.3.2'
      ],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.6'
      ])
