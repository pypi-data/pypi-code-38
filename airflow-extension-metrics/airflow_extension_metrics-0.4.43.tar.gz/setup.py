import os
from setuptools import setup, find_packages


os.environ['SLUGIFY_USES_TEXT_UNIDECODE'] = 'yes'

setup(name='airflow_extension_metrics',
      version='0.4.43',
      description='Package to expand Airflow for custom metrics.',
      url='https://github.com/nytm/airflow_extensions/custom_metrics',
      author='Sarah Duncan',
      author_email='sarah.duncan@nytimes.com',
      license='Apache License 2.0',
      packages=['custom_metrics', 'custom_metrics.helpers', 'custom_metrics.airflow'],
      zip_safe=False,
      install_requires=[
          'google-cloud-monitoring==0.31.1'  # for extended logging
      ],
      )
