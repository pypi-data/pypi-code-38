# -*- coding: utf-8 -*-
"""
@author: Jussi (jnu@iki.fi)
"""

from setuptools import setup, find_packages


setup(name='ulstools',
      version='0.10.4',
      description='Miscellaneous tools for ULS',
      author='Jussi Nurminen',
      author_email='jnu@iki.fi',
      license='GPLv3',
      url='https://github.com/jjnurminen/ulstools',
      packages=find_packages(),
      entry_points={
            'console_scripts': ['pdfmerger=ulstools.apps.pdfmerger.pdfmerger:main',
                                'pdfmerger_make_shortcut=ulstools.apps.pdfmerger.pdfmerger:make_my_shortcut']
                  },
      include_package_data=True,
      )
