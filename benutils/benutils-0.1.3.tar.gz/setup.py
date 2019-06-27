from setuptools import setup

from benutils.version import __version__


setup(name='benutils',
      version=__version__,
      packages=['benutils.misc',
                'benutils.widget',
                'benutils.sdr'],
      install_requires=['pyusb==1.0.0a3', 'numpy'],
      url='https://gitlab.com/bendub/benutils',
      author='Benoit Dubois',
      author_email='benoit.dubois@femto-st.fr',
      description='Various utilities (mjd, data container, widgets...)',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
          'Natural Language :: English',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering'],
)
