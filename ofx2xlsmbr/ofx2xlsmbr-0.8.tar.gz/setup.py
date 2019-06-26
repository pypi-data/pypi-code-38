from distutils.core import setup
setup(
  name = 'ofx2xlsmbr',         # How you named your package folder (MyLib)
  packages = ['ofx2xlsmbr', 
    'ofx2xlsmbr.factory', 
    'ofx2xlsmbr.model', 
    'ofx2xlsmbr.reader',
    'ofx2xlsmbr.reader.xml',
    'ofx2xlsmbr.writer',
    'ofx2xlsmbr.writer.xlsm'],   # Chose the same as "name"
  version = '0.8',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Convert ofx to xlsm',   # Give a short description about your library
  author = 'Rafael Musmanno',                   # Type in your name
  author_email = 'rafa.musmanno@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/rmusmanno/ofx2xlsmbr/',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/rmusmanno/ofx2xlsmbr/archive/v0.8.tar.gz',    # I explain this later on
  keywords = ['ofx', 'xlsm'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
        'et-xmlfile',
        'jdcal',
        'openpyxl',
        'ofxtoolslambda',
        'pytz',
        'lxml',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package

    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',

    'License :: OSI Approved :: MIT License',   # Again, pick a license

    'Programming Language :: Python :: 3.7',      #Specify which pyhton versions that you want to support
  ],
)