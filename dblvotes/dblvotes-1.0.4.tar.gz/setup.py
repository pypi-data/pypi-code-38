from distutils.core import setup
setup(
  name = 'dblvotes',         # How you named your package folder (MyLib)
  packages = ['dblvotes'],   # Chose the same as "name"
  version = '1.0.4',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'API for DiscordBots to help with not needing webhooks.',   # Give a short description about your library
  author = 'LazyNeko',                   # Type in your name
  author_email = 'nekobot.help@gmail.com',      # Type in your E-Mail
#  url = 'https://github.com/LazyNeko1/nbapi',   These commented out ones are for my other api i made :p
#  download_url = 'https://github.com/LazyNeko1/nbapi/archive/0.0.1.tar.gz', if you are curious about it, `pip install nbapi` :3
  keywords = ['DiscordBotList'],   # Keywords that define your package best
  zip_safe=False,
  include_package_data=True,

  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
