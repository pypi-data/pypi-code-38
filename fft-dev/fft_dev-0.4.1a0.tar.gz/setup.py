# Set __version__ in the setup.py
with open('fft_dev/version.py') as f: exec(f.read())

from setuptools import setup

setup(name='fft_dev',
      description='Driver and UI for 3562A and 35670A FFT analyzer',
      version=__version__,
      packages=['fft_dev',
                'fft_dev.fft3562a',
                'fft_dev.fft35670a'],
      scripts=["bin/fft35670a-gui",
               "bin/fft3562a-gui"],
      requires=['PyQt5', 'numpy', 'pyqtgraph', 'iopy'],
      url='https://gitlab.com/bendub/fft_dev',
      author='Benoit Dubois',
      author_email='benoit.dubois@femto-st.fr',
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'],)
