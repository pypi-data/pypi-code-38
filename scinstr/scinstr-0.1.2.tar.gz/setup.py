# Set __version__ in the setup.py 
with open('scinstr/version.py') as f: exec(f.read())

from setuptools import setup

setup(name='scinstr',
      description='A package dedicated to handle various scientific instruments (multimeter, frequency counter, acquisition unit...)',
      version=__version__,
      packages=['scinstr'],
      scripts=['bin/dmm-cli'],
      extra_require=['PyQt5', 'pyserial', 'python-usbtmc'],
      url='https://gitlab.com/bendub/scinstr',
      author='Benoit Dubois',
      author_email='benoit.dubois@femto-st.fr',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
          'Natural Language :: English',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering'
          ]
)
