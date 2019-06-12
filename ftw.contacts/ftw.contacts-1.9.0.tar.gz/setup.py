from setuptools import find_packages
from setuptools import setup

import os

version = '1.9.0'
maintainer = 'Mathias Leimgruber'

tests_require = [
    'ftw.builder',
    'plone.app.testing',
    'ftw.testbrowser',
    'ftw.contacts [zip_export, simplelayout, geo, ldap]',
    'unittest2',
    'ftw.testing',
    ]
zip_export = [
    'ftw.zipexport',
    ]
simplelayout = [
    'ftw.simplelayout [contenttypes]',
    'ftw.referencewidget',
    ]
geo = [
    'ftw.geo',
    'collective.geo.openlayers >= 3.2b1',
    'collective.geo.bundle [dexterity]',
    ]
ldap = [
    'python-ldap<=2.4.25',
    'Products.PloneLDAP',
    'Products.LDAPUserFolder < 3a',
    ]
extras_require = {
    'tests': tests_require,
    'zip_export': zip_export,
    'simplelayout': simplelayout,
    'geo': geo,
    'ldap': ldap,
    'plone4': [
        'plone.app.referenceablebehavior',
    ],
    }

setup(name='ftw.contacts',
      version=version,
      description='Provides a contact-contenttype',
      long_description=open(
          'README.rst').read() + '\n' + open(
          os.path.join('docs', 'HISTORY.txt')).read(),

      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Framework :: Plone',
          'Framework :: Plone :: 4.2',
          'Framework :: Plone :: 5.1',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],

      keywords='ftw plone contacts',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/ftw.contacts',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', ],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
          'Plone',
          'z3c.schema',
          'setuptools',
          'collective.dexteritytextindexer',
          'collective.js.jqueryui',
          'plone.app.relationfield',
          'plone.api >= 1.3.3',
          'ftw.zipexport',
          'ftw.autofeature',
          'ftw.upgrade',
          ],

      tests_require=tests_require,
      extras_require=extras_require,

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone

      [plone.recipe.zope2instance.ctl]
      sync_contacts = ftw.contacts.sync.command:do_sync_profiles
      """,
      )
