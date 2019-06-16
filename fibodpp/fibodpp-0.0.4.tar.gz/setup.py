from distutils.core import setup
setup(
  name = 'fibodpp',         # How you named your package folder (MyLib)
  packages = ['fibodpp'],   # Chose the same as "name"
  version = '0.0.4',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Python fibonacci example',   # Give a short description about your library
  author = 'Olha Solovei',                   # Type in your name
  author_email = 'olya.slv.os@gmail.com',      # Type in your E-Mail
  url = '',   # Provide either the link to your github or to your website
  download_url = '',    # I'll explain this later on
  keywords = ['pwr', 'fibonacci', 'dpp'],   # Keywords that define your package best
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
  ],
)