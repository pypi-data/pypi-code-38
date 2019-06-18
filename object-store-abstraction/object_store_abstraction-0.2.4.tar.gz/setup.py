from setuptools import setup
import versioneer

#Dependancy lists maintained here and in tox.ini
sp_install_requires = [
  'pytz==2018.4',
  'sortedcontainers==1.5.9',
  'pyjwt==1.7.1',
  'sqlalchemy==1.3.1',
  'PyMySQL==0.9.3',
  'python-dateutil==2.7.2'
]
sp_tests_require = [
  'nose==1.3.7'
]

all_require = sp_install_requires + sp_tests_require

setup(name='object_store_abstraction',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Python package which provides an abstract object store',
      url='https://github.com/rmetcalf9/object_store_abstraction',
      author='Robert Metcalf',
      author_email='rmetcalf9@googlemail.com',
      license='MIT',
      packages=['object_store_abstraction'],
      zip_safe=False,
      install_requires=sp_install_requires,
      tests_require=sp_tests_require,
      include_package_data=True)
