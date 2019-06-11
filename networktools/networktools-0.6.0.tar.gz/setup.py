from setuptools import setup
file_req = './requeriments.txt'
requeriments = []
with open(file_req, 'r') as file:
    reader = file.readlines()
    for line in reader:
        requeriments.append(line.replace('\n', ''))


setup(name='networktools',
      version='0.6.0',
      description='NetworkTools are some special functions to help with software developing',
      url='http://gitlab.csn.uchile.cl/dpineda/networktools',
      author='David Pineda Osorio',
      author_email='dpineda@csn.uchile.cl',
      license='GPL3',
      install_requires=[],
      packages=['networktools'],
      zip_safe=False)
