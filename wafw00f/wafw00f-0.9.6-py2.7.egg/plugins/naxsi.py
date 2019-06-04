#!/usr/bin/env python

NAME = 'Naxsi'

def is_waf(self):
	# Sometimes naxsi waf returns 'x-data-origin: naxsi/waf'
    if self.matchheader(('X-Data-Origin', '^naxsi(.*)?')):
    	return True
    # Found samples returning 'server: naxsi/2.0'
    if self.matchheader(('server', 'naxsi(.*)?')):
    	return True
    for attack in self.attacks:
        r = attack(self)
        if r is None:
            return
        _, responsebody = r
        if any(i in responsebody for i in (b'Blocked By NAXSI', b'Naxsi Blocked Information')):
            return True
    return False