from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='autoschedule',
      version='0.1',
      description='Generate schedule, talks, speakers page automatically like official Pycon thailand 2019 website: https://th.pycon.org',
      long_description=readme(),
      long_description_content_type='text/markdown',
      url='https://github.com/Chomtana/autoschedule',
      author='Chomtana',
      author_email='Chomtana001@gmail.com',
      license='MIT',
      install_requires=[
          'docutils',
          'pyyaml',
      ],
      keywords='autoschedule schedule generator codegenerator schedulepage talks talkspage speakers speakerspage pycon'.split(' '),
      packages=['autoschedule'],
      package_dir={'autoschedule': '.'},
      package_data={'autoschedule': ['ScheduleShortcode.py','ScheduleShortcode.plugin']},
      )
