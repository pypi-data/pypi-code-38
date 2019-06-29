from .wms import WMS
from .session import session

wms = wms.WMS()
# Create a session object accessible via wms.session
wms.session = session(WMS)
version='0.0.0.5'
