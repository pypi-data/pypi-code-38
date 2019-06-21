import time
import channel_access.common as ca
import channel_access.server as cas

with cas.Server() as server:
    pv = server.createPV('CAS:Test', ca.Type.LONG)
    while True:
        pv.value += 1
        time.sleep(1.0)
