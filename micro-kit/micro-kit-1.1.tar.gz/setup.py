from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
  name='micro-kit',
  packages=find_packages(),
  version='1.1',
  license='GNU General Public License',    
  description='A helper kit to power the APIs',
  author='Ayush Aggarwal',
  author_email='ayushaggarwal.97@gmail.com',
  url='https://github.com/innovaccer/microkit',
  download_url='https://github.com/innovaccer/microkit/archive/V1.0.tar.gz',
  keywords=['python', 'flask', 'response', 'logger'],
  install_requires=["flask", ],
  classifiers=[
    'Development Status :: 3 - Alpha', 
    'Intended Audience :: Developers',    
    'Topic :: Software Development :: Build Tools',
    'Programming Language :: Python :: 2.7', 

  ],
)
