from distutils.core import setup
setup(
  name = 'mapartmwc',         # How you named your package folder (MyLib)
  packages = ['mapartmwc'],   # Chose the same as "name"
  version = '1.2',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Download movies of your choice',   # Give a short description about your library
  author = 'Lucifer_cipher',                   # Type in your name
  author_email = 'praneetquantumx@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/PraneetNeuro/popcorn_mp',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/PraneetNeuro/popcorn_mp/archive/1.0.tar.gz',    # I explain this later on
  keywords = ['entertainment', 'movies', 'netflix'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
      ],
  scripts=['map.py'],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',    'License :: OSI Approved :: MIT License',   # Again, pick a license    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
