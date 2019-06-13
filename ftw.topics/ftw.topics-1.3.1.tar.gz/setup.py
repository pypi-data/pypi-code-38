import os
from setuptools import setup, find_packages


version = '1.3.1'


extras_require = {
    'simplelayout': [
        'simplelayout.base',
        'ftw.contentpage'],

    'archetypes': [
        'Products.Archetypes',
        'archetypes.schemaextender',
        'archetypes.referencebrowserwidget',
        ]}


tests_require = [
    'unittest2',
    'mocker',
    'pyquery',
    'ftw.testing [splinter] <= 1.11.0',
    'ftw.testbrowser',
    'ftw.builder',

    'zope.i18n',
    'z3c.autoinclude',
    'transaction',
    'zope.traversing',
    'AccessControl',
    'zope.configuration',

    'plone.uuid',
    'plone.testing',
    'plone.app.testing',

    'ftw.inflator [dexterity]',
    ] + reduce(list.__add__, extras_require.values())

extras_require['tests'] = tests_require


setup(name='ftw.topics',
      version=version,
      description='Create subject trees in Plone',

      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw topics',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.topics',

      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', ],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',

        'zope.schema',
        'zope.interface',
        'zope.component',
        'zope.i18nmessageid',
        'Acquisition',
        'Zope2',
        'zc.relation',

        'Plone',
        'plone.app.layout',
        'plone.browserlayer',
        'plone.memoize',
        'Products.GenericSetup',
        'Products.CMFCore',
        'Products.CMFPlone',

        'plone.autoform',
        'plone.behavior',
        'plone.dexterity',
        'plone.app.dexterity',
        'plone.app.relationfield',
        'collective.dexteritytextindexer',
        'collective.geo.openlayers >= 3.0, < 4.0',
        'collective.geo.mapwidget >= 2.1, < 3.0',
        'plone.app.referenceablebehavior',
        'plone.directives.form',

        'ftw.upgrade',
        'ftw.referencewidget',
        ],

      tests_require=tests_require,
      extras_require=extras_require,

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
