from setuptools import setup, find_packages

version = '0.41'
name = 'slapos.recipe.build'
long_description = open("README.rst").read() + "\n" + \
    open("CHANGELOG.rst").read() + "\n"

# extras_requires are not used because of
#   https://bugs.launchpad.net/zc.buildout/+bug/85604
setup(name=name,
      version=version,
      description="Flexible software building recipe.",
      long_description=long_description,
      classifiers=[
          "Framework :: Buildout :: Recipe",
          "Programming Language :: Python",
        ],
      keywords='slapos recipe',
      license='GPLv3',
      url='https://lab.nexedi.com/nexedi/slapos.recipe.build',
      namespace_packages=['slapos', 'slapos.recipe'],
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
        'setuptools', # namespaces
        'zc.buildout', # plays with buildout
        ],
      extras_require={
        'test' : ['zope.testing'],
      },
      tests_require = ['zope.testing'],
      test_suite = '%s.tests.test_suite' % name,
      zip_safe=True,
      entry_points={
        'zc.buildout': [
          'default = slapos.recipe.build:Script',
          'download = slapos.recipe.download:Recipe',
          'download-unpacked = slapos.recipe.downloadunpacked:Recipe',
          'gitclone = slapos.recipe.gitclone:Recipe',
          'npm = slapos.recipe.npm:Npm',
          'vm.install-debian = slapos.recipe.vm:InstallDebianRecipe',
          'vm.run = slapos.recipe.vm:RunRecipe',
        ],
        'zc.buildout.uninstall': [
          'gitclone = slapos.recipe.gitclone:uninstall',
        ],
        },
    )
