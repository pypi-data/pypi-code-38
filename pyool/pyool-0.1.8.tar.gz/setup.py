from distutils.core import setup


setup(
  name = 'pyool',         # How you named your package folder (MyLib)
  packages = ['pyool'],   # Chose the same as "name"
  version = '0.1.8',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Python package for Optimized ODPS ',   # Give a short description about your library
  author = 'Loc Nguyen',                   # Type in your name
  author_email = 'loc.nguyen14061996@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/locnguyen14061996/pyool',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/locnguyen14061996/pyool/archive/0.1.7.tar.gz',    # I explain this later on
  keywords = ['Python', 'ODPS', 'pyool'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'odps',
          'psycopg2',
          'mysql-connector',
          'pandas',
          'datetime',
          'uuid',
          'requests',
          'O365'
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers 
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.6'     #Specify which pyhton versions that you want to support
  ],
)