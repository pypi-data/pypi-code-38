from setuptools import find_packages, setup
import pathlib
import os

MAIN_DIR = pathlib.Path(__file__).absolute().parent

packages = find_packages(
  str(MAIN_DIR),
  include=('page_block*',),
)

# Did I mention that setup.py is not finest piece of software on earth.
# For this to work when installed you'll need to enumerate all template and static file.


def read_dir(package: str, dir: str):
  package_root = os.path.abspath(package.replace(".", "/"))
  dir = os.path.join(package_root, dir)
  res = []
  for root, subFolders, files in os.walk(dir):
    for file in files:
      res.append(
        os.path.relpath(
         os.path.join(root, file),
         package_root
        ))

  return res


if __name__ == "__main__":

  setup(
    name='page_block',
    version='1.0.6',
    packages=packages,
    license='MIT',
    author='Jacek Bzdak',
    author_email='jacek@askesis.pl',
    description='Simple CMS-like app that allows you to dump admin editable blocks '
                'of markdown into pages via template tag.',
    install_requires=['django', 'simple-django-tag-parser', 'django-model-utils'],
    package_data={
      package: [] +
        read_dir(package, "static") +
        read_dir(package, "templates")
      for package in packages
    },
    include_package_data=True
)
