from distutils.core import setup
setup(
  name = 'tb-ble-adapter',
  version = '1.2',
  license='Apache',
  description = 'Ble adapter demo, that connects to available devices and sends data from them to thingsboard server',
  author = 'ThingsBoard',
  author_email = 'info@thingsboard.io',
  url = 'https://github.com/thingsboard/tb-ble-adapter',
  download_url = 'https://github.com/thingsboard/tb-ble-adapter/archive/1.2.tar.gz',
  keywords = ['tb-ble-adapter', 'demo', 'bluetooth low energy'],
  install_requires=[
          'btlewrap',
          'bluepy',
          'tb-mqtt-client',
      ],
  classifiers=[
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 3.4',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent',
  ],
)
