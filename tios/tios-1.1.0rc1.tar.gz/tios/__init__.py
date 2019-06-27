import os

try:
    import popylar
    popylar.track_event('UA-102907451-1', 'import', 'import_tios')
except ImportError:
    pass

TIOS_CONFIGDIR = os.getenv('TIOS_CONFIGDIR', 
                           os.path.join(os.getenv('HOME'), '.tios'))
TIOS_CONFIGFILE = os.path.join(TIOS_CONFIGDIR, 'tios.cfg')
if os.path.exists(TIOS_CONFIGFILE):
    permissions = os.stat(TIOS_CONFIGFILE).st_mode & 0o777
    if permissions & 0o077 > 0:
        message = ('Error - your tios configuration file {} '+
                   'has permissions {} - it must be readable ' +
                   'only by you.')
        raise RuntimeError(message.format(TIOS_CONFIGFILE, 
                                          oct(permissions & 0o777)))

