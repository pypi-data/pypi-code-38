from setuptools import setup, find_packages
import os

product_path = os.path.join('Products', 'TIDStorage')

version = open(os.path.join(product_path, 'VERSION.txt')).read().split()[-1]

setup(name='Products.TIDStorage',
      version=version,
      description="TIDStorage Product provides a way to have consistent "\
           "backups when running a multi-storage instance (only ZEO is "\
           "supported at the moment).",
      long_description=open(os.path.join(product_path, 'README')).read() + "\n" + \
                       open(os.path.join(product_path, 'CHANGES')).read(),
      classifiers=[
        "Framework :: Zope2",
        "Operating System :: OS Independent",
        ],
      keywords='Zope TIDStorage',
      author='Vincent Pelletier',
      author_email='vincent@nexedi.com',
      url='https://svn.erp5.org/repos/public/erp5/trunk/utils/Products.TIDStorage/',
      packages=find_packages(),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Zope2',
      ],
      entry_points={
        'console_scripts': [
          'tidstoraged = Products.TIDStorage.bin.tidstorage:main',
          'tidstorage_repozo = Products.TIDStorage.repozo.repozo_tidstorage:main',
          'tidstorage_restore = Products.TIDStorage.repozo.restore_tidstorage:main',
        ]
      }
      )
