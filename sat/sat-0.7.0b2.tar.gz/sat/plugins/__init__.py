# XXX: the Monkey Patch is here and not in src/__init__ to avoir issues with pyjamas compilation
# TODO: remove this when changes are merged in Wokkel
from sat_tmp.wokkel import install
install()
