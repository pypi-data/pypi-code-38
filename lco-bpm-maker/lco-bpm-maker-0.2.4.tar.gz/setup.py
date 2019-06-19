from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='lco-bpm-maker',
      author='Matt Daily',
      author_email='mdaily@lco.global',
      url='https://github.com/LCOGT/pixel-mask-gen',
      description='LCO bad pixel mask creator',
      long_description=long_description,
      long_description_content_type='text/markdown',
      version='0.2.4',
      packages=find_packages(),
      setup_requires=['pytest-runner'],
      install_requires=['numpy', 'astropy', 'lcogt-logging'],
      tests_require=['pytest', 'pytest-cov'],
      entry_points={'console_scripts': ['lco_bpm_maker=bpm.generate_bpm:generate_bpm']})
