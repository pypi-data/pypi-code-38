'''
Package definition for 'angda'.
'''

VERSION_DATE   = '2019-06-15'
VERSION_NUMBER = '0.1.0a1'
VERSION        = f'Angda version {VERSION_NUMBER} ({VERSION_DATE}).'

from angda import apis
from angda import items
from angda import tools

from angda.apis  import roll
from angda.items import Dice, Roll
