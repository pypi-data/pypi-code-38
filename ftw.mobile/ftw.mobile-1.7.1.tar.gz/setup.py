from setuptools import setup, find_packages
import os

version = '1.7.1'
maintainer = 'Mathias Leimgruber'

tests_require = [
    'Products.CMFPlone',
    'ftw.builder',
    'ftw.testbrowser>=1.23.0',
    'ftw.testing',
    'transaction',
    'plone.app.multilingual',
    'unittest2',
]

extras_require = {
    'tests': tests_require,
    'test': tests_require,
}


setup(name='ftw.mobile',
      version=version,
      description='Mobile navigation and a basic infrastructure'
      ' for mobile buttons on a Plone site.',
      long_description=open('README.rst').read() + '\n' +
      open(os.path.join('docs', 'HISTORY.txt')).read(),

      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Framework :: Plone',
          'Framework :: Plone :: 4.3',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],

      keywords='ftw plone mobile navigation',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/ftw.mobile',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', ],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
          'AccessControl',
          'Acquisition',
          'Persistence',
          'Plone',
          'Products.CMFCore',
          'Zope2',
          'ftw.gopip',
          'ftw.theming >= 1.6.0',
          'ftw.upgrade',
          'plone.api',
          'plone.uuid',
          'setuptools',
          'zExceptions',
          'zope.annotation',
          'zope.component',
          'zope.event',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.lifecycleevent',
          'zope.publisher',
      ],

      tests_require=tests_require,
      extras_require=extras_require,

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
