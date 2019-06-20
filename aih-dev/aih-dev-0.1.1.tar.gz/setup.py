from setuptools import setup

setup(name='aih-dev',
      version='0.1.1',
      description='',
      author='dien.duong',
      author_email='duongngocdien@gmail.com',
      license='MIT',
      packages=['aih'],
      install_requires=[
          'PyJWT',
          'requests'
      ],
      zip_safe=False)
