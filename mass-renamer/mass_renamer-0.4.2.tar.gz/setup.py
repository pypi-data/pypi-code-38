from distutils.core import setup

setup(
  name = 'mass_renamer',
  packages = ['mass_renamer'],
  version = '0.4.2',
  license='MIT',
  description = 'A Python script to mass rename files in a directory.',
  author = 'Matthew Kleiner',
  url = 'https://github.com/mrniceguy127/mass-renamer',
  keywords = ['renamer', 'rename', 'file system'],
  entry_points = {
    "console_scripts": [
      "mass-renamer=mass_renamer:main",
    ]
  },
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
)
