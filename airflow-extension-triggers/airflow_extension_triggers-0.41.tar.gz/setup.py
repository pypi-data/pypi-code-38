import os
from setuptools import setup, find_packages


os.environ['SLUGIFY_USES_TEXT_UNIDECODE'] = 'yes'

setup(name='airflow_extension_triggers',
      version='0.41',
      description='Package to expand Airflow for triggering events.',
      url='https://github.com/nytm/airflow_extensions/event_triggering',
      author='Sarah Duncan',
      author_email='sarah.duncan@nytimes.com',
      license='Apache License 2.0',
      packages=['event_triggering'],
      zip_safe=False,
      install_requires=[
          'tzlocal<2.0.0.0,>=1.5.0.0',  # avoids "error: tzlocal 2.0.0b1 is installed but tzlocal<2.0.0.0,>=1.5.0.0 is required by {'pendulum'}"
          #'apache-airflow==1.10.1',  # 1.10.0 has a version conflict "error: Flask-Login 0.2.11 is installed but Flask-Login<0.5,>=0.3 is required by {'flask-appbuilder'}"
      ],
      )
