import setuptools

VERSION = '0.1.5'

with open("README.md", "r") as fh:
    long_description = fh.read()

pkgs = setuptools.find_packages()
pkgs.remove('lib.test')
pkgs.append('assets')

setuptools.setup(
     name='byu-auvsi-imaging-client',
     version=VERSION,
     scripts=['gui.py'],
     entry_points={
        'gui_scripts': [
            'img_gui = gui:main',
        ]
     },
     author="BYU AUVSI Team",
     author_email="tylerm15@gmail.com",
     description="Imaging Client GUI for manual classification",
     install_requires=['requests==2.20.1', 'pillow==5.3.0', 'opencv-python==3.4.2.*', 'ttkthemes==2.2.0', 'imutils==0.5.2'],
     long_description=long_description,
     long_description_content_type="text/markdown",
     packages=pkgs,
     package_data={
        '': ['*.png', '*.jpg'],
     },
     url="https://github.com/BYU-AUVSI/imaging",
     classifiers=[
         "Programming Language :: Python :: 3",
         "Operating System :: OS Independent",
         "Programming Language :: Python :: 3.5",
         "Programming Language :: Python :: 3.6",
         "Programming Language :: Python :: 3.7",
     ],
 )
