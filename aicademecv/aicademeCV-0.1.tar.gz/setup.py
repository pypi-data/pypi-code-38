from distutils.core import setup
setup(
  name = 'aicademeCV',         # How you named your package folder (MyLib)
  packages = ['aicademeCV'],   # Chose the same as "name"
  version = '0.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Image processing library with a specific focus on data preparation for skin based deep learning projects',   # Give a short description about your library
  author = 'Suyash Dixit, Nishtha Gupta',                   # Type in your name
  author_email = 'suyash@aicademe.com',      # Type in your E-Mail
  url = 'https://github.com/suyash091/aicademeCV',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/suyash091/aicademeCV/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['image', 'skin', 'detection','segmentation', 'patches', 'lesion','crop','augmentation','recognition','data','processing','preprocessing','preparation','deep','learning','neural','networks'],   # Keywords that define your package best
  ##install_requires=[            # I get to this in a second
  ##        'cv2',
  ##        'numpy','os',
  ##    ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
 )
