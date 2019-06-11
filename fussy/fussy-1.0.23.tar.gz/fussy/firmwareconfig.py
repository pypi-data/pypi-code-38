"""Load firmware configuration so that we can find out firmware metadata

Expected keys:

    [fussy]
    product=sample
    keyring=/etc/fussy/keys
    extra_etc=/etc/%(product)s
    var_directory=/var/%(sample)s
    firmware_directory=/opt/%(sample)s
"""
import glob
try:
    import ConfigParser as configparser 
except ImportError:
    import configparser

options = None
def loadoptions(product='fussy'):
    global options
    if options is None:
        options = configparser.SafeConfigParser( )
        options.read( sorted(glob.glob( '/etc/fussy/*.conf' )))
        try:
            product = options.get( 'fussy','product' )
        except (configparser.NoSectionError,configparser.NoOptionError) as err:
            pass 
        else:
            options.read( sorted(glob.glob( '/etc/%(product)s/*.conf'%locals() ) ))
    return options 

def getstring( section, key, default=None ):
    if not options:
        raise RuntimeError( "Need to load options first")
    try:
        return options.get( section, key )
    except (configparser.NoSectionError,configparser.NoOptionError):
        return default 
def getboolean( section, key, default=None ):
    if not options:
        raise RuntimeError( "Need to load options first")
    try:
        return options.getboolean( section, key )
    except (configparser.NoSectionError,configparser.NoOptionError):
        return default 
