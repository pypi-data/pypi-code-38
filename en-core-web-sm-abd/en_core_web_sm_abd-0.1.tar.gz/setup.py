from distutils.core import setup
setup(
  name = 'en_core_web_sm_abd',         # How you named your package folder (MyLib)
  packages = ['en_core_web_sm_abd'],   # Chose the same as "name"
  version = '0.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'small dictionary for spacy',   # Give a short description about your library
  author = 'Benjamin Johnson',                   # Type in your name
  author_email = 'benjaminallanjohnson@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/g3n3ralb3n-wp/en_core_web_sm_abd',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/g3n3ralb3n-wp/en_core_web_sm_abd/archive/v0.1.tar.gz',    # I explain this later on
  keywords = ['SOME', 'MEANINGFULL', 'KEYWORDS'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'spacy',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.6',      #Specify which pyhton versions that you want to support
  ],
)
