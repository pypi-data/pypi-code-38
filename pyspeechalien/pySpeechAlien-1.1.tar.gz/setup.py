from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='pySpeechAlien',
      version='1.1',
      description='Speech analysis tool',
      long_description=long_description,
      url='https://github.com/arpansahoo/pySpeechAlien',
      author='Arpan Sahoo',
      author_email='asahoo1@jhu.edu',
      license='MIT',
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
	  keywords='praat speech signal processing phonetics',
	  install_requires=[
		'numpy>=1.15.2',
		'praat-parselmouth>=0.3.2',
		'pandas>=0.23.4',
		'scipy>=1.1.0',
		],
	  packages=['pySpeechAlien'],
      zip_safe=False
)
