from setuptools import setup

version = "0.0.87"
setup(name='planblick',
      version=version,
      description='',
      url='https://www.planblick.com',
      author='Florian Kröber @ Planblick',
      author_email='fk@planblick.com',
      license='MIT',
      packages=['planblick.httpserver', 'planblick.autorun', 'planblick.sqs', 'planblick.sns', 'planblick.logger',
                'planblick.encryption', 'planblick.helpers'],
      install_requires=[
          'cherrypy',
          'requests',
          'boto3',
          'flask'
      ],
      zip_safe=False)
