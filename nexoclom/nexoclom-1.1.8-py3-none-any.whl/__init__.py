from .Input import Input
from .Output import Output
from .modeldriver import modeldriver
from .LOSResult import LOSResult
from .produce_image import ModelImage
from .configure_model import configure_model
from .IDLout import IDLout


name = 'nexoclom'
__author__ = 'Matthew Burger'
__email__ = 'mburger@stsci.edu'
__version__ = '1.1.8'
database = 'thesolarsystemmb'


try:
    configure_model(force=False)
except:
    print('Database not set up')
