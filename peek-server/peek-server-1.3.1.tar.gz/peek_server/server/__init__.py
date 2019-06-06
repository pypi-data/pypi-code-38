from txhttputil.util.ModuleUtil import filterModules

for mod in filterModules(__name__, __file__):
    __import__(mod, locals(), globals())

from . import sw_download
from . import sw_install
from . import sw_upload
from . import sw_version
