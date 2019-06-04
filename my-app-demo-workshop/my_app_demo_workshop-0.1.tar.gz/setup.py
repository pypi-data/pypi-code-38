from setuptools import setup
from setuptools import find_packages

setup(name='my_app_demo_workshop',
      version='0.1',
      description='Demo app for Python workshop',
      url='https://github.com/rusugheorghe/my_app_demo_workshop',
      author='Gheorghe Rusu',
      author_email='gheorghe.rusu@endava.com',
      license='MIT',
      include_package_data=True,
      packages=find_packages(),
      python_requires='>=3.6',
      install_requires=['flask==1.0.2'],
      entry_points={
              'console_scripts': ['my_app=my_app_demo_workshop.my_app:main'],
          },
      zip_safe=False)
