from . import install
from os_sys import download, upload
from . import make_install_file as _mil
import os
import sys
def auto_install():
    error = True
    while error:
        package = input('what package you want to install:\n')
        try:
            print('downloading install file...')
            download.download('https:#my page/%s' % str(package + '.py_install'), os.path.join(os.path.abspath(''), 'buildfile.py_install'))
            print('downloading info file...')
            download.download('https:#my page/%s' % str(package + '.info'), os.path.join(os.path.abspath(''), 'buildfile.info'))
        except Exception:
            print('error file or package doesn\'t exist', file=sys.stderr)
            continue
        else:
            print('starting installation...')
            install(os.path.abspath(''))
