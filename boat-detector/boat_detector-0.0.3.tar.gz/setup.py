from setuptools import setup, find_packages

setup(name='boat_detector',
      version='0.0.3',
      description="Python scripts for detecting noise made by boats in broadband hydrophone data",
      url='https://gitlab.meridian.cs.dal.ca/data_analytics_dal/packages/boat_detector',
      author='Oliver Kirsebom, Fabio Frazao',
      author_email='oliver.kirsebom@dal.ca, fsfrazao@dal.ca',
      license='GNU General Public License v3.0',
      packages=find_packages(),
      install_requires=[
          'ketos==1.0.3',
          ],
      entry_points = {"console_scripts": ["audio-filterer=bin.audio_filterer:main", "anomaly-detector=bin.anomaly_detector:main"]},
      include_package_data=True,
      zip_safe=False)
