from distutils.core import setup

setup(
    name = 'CTSScript',
    packages = ['CTSScript'],
    version = '1.0.1',
    description = 'The tool is for parsing CTS report and automatically running/retrying CTS process.',
    author = 'Dramon Studio',
    author_email = 'yang1365g@gmail.com',
    url = 'https://github.com/DramonStudio/CTSScript',
    download_url = 'https://github.com/DramonStudio/CTSScript/archive/v_01.tar.gz',
    keywords = ['CTS','Google','Parser'],
    install_requires=[          
          'httpimport',
      ]
)