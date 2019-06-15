from setuptools import setup

setup(name='zynet',
      version='0.1',
      description='Zynet FPGA DNN generator package',
      url='https://github.com/dsdnu/zynet',
      author='',
      author_email='',
      license='MIT',
      packages=['zynet'],
      package_dir={'zynet': 'zynet'},
      package_data={'zynet': ['db/*']},
      zip_safe=False)