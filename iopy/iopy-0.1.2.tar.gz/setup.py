# Set __version__ in the setup.py 
with open('iopy/version.py') as f: exec(f.read())

from setuptools import setup

setup(name='iopy',
      description='iopy is a (small) library providing input/output capabilities',
      version=__version__,
      packages=['iopy'],
      extras_require={
          'fx2': ['pyusb==1.0.0a3'],
          'smdp': ['pyserial'],
      },
      url='https://gitlab.com/bendub/iopy',
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
