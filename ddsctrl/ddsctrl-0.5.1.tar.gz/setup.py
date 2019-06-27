# Set __version__ in the setup.py 
with open('ddsctrl/version.py') as f: exec(f.read())

from setuptools import setup

setup(name='ddsctrl',
      description='ddscontroller allow basic handling of AD9912 DDS development board.',
      version=__version__,
      packages=['ddsctrl'],
      scripts=["bin/ddscontroller"],
      require=['PyQt5', 'ad9xdds'],
      url='https://gitlab.com/bendub/ddsctrl',
      author='Benoit Dubois',
      author_email='benoit.dubois@femto-st.fr',
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering']
)
