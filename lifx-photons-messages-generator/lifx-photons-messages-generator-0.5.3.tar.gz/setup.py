from setuptools import setup, find_packages

from photons_messages_generator import VERSION

setup(
      name = "lifx-photons-messages-generator"
    , version = VERSION
    , packages = ["photons_messages_generator"] + ["photons_messages_generator.{0}".format(pkg) for pkg in find_packages("photons_messages_generator")]
    , include_package_data = True

    , install_requires =
      [ "delfick_error==1.7.8"
      , "input_algorithms==0.6.0"
      , "option_merge==1.6"
      , "ruamel.yaml==0.15.87"
      , "delfick_logging==0.3.2"
      ]

    , extras_require =
      { "tests":
        [ "noseOfYeti>=1.7"
        , "nose"
        ]
      }

    , entry_points =
      { 'console_scripts' :
        [ 'generate_photons_messages = photons_messages_generator.executor:main'
        ]
      }

    # metadata for upload to PyPI
    , url = "http://github.com/delfick/photons-messages-generator"
    , author = "Stephen Moore"
    , author_email = "delfick755@gmail.com"
    , description = "Code for generating the photons_messages module"
    , long_description = open("README.rst").read()
    , license = "MIT"
    , keywords = "lifx photons"
    )
