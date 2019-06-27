# Set __version__ in the setup.py 
with open('ad9xdds/version.py') as f: exec(f.read())

from setuptools import setup

setup(name='ad9xdds',
      desscription='Ad9xDds is library dedicated to handle AD9854 and AD9912 development board.',
      version=__version__,
      packages=['ad9xdds'],
      extras_require={
          'ad9912dev': ['iopy'],
          'ad9854dev': ['pyparallel'],
          'qad9912dev': ['PyQt5'],
      },
      url='https://gitlab.com/bendub/ad9xdds',
      author='Benoit Dubois',
      author_email='benoit.dubois@femto-st.fr',
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering']
)
