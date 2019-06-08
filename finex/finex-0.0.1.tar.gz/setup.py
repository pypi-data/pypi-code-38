from setuptools import setup

setup(name = "finex",
      version = "0.0.1",
      url = "",
      license = "BSD",
      description = "Python Ecosystem for Financial Analysis",
      long_description = "",
      author = "Mehmet Dogan",
      author_email = "m.dogan@mail.com",
      install_requires = "",
      zip_safe = False,
      platforms = 'any',
      classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
      ],
      entry_points={
        'console_scripts': [
            'finex=finex:main',
        ],
      },
      packages = ['finex']
      )

_author_ = "Mehmet Dogan"
