from distutils.core import setup
setup(
  name = 'jComLib',         # How you named your package folder (MyLib)
  packages = ['jComLib'],   # Chose the same as "name"
  version = '3',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Basic Mail Communication Library',   # Give a short description about your library
  author = 'Masterbond7',                   # Type in your name
  author_email = 'quintinslough@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/Masterbond7/jComLib.git',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/Masterbond7/jComLib/archive/3.tar.gz',    # I explain this later on
  keywords = ['Communication', 'Mail', 'Basic', 'Gmail'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
      ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.7',      #Specify which pyhton versions that you want to support
  ],
)
