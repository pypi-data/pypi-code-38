'''Module to handle Spectre Zones'''
import ipaddress
from distutils.version import LooseVersion
import math
import spectreapi
import json

class Zone:
    '''Class abstracts out Spectre Zones
    Zones are basically a collection of Collectors.
    They're useful for grouping sets of results together'''
    def __init__(self, id_num, name, description=None, server=None):
        self.id_num = id_num
        self.name = name
        self.description = description
        self.server = server

    def __repr__(self):
        return 'Zone(%d, "%s", "%s")' % (self.id_num, self.name, self.description)

    def __str__(self):
        return 'id=%d, name=%s, description=%s)' % (self.id_num, self.name, self.description)

    def _get_cidrs(self, cidr_type):
        if cidr_type not in ('known', 'trusted', 'internal', 'avoid'):
            raise spectreapi.InvalidArgument('%s is not a valid type for _get_cidrs')

        if self.server is None:
            raise spectreapi.NoServerException(
                'Collector.getCidrs() requires a Collector with a server')

        cidrs = []
        results = self.server.get('zone/%d/cidr/%s' % (self.id_num, cidr_type))
        for cidr in results:
            cidrs.append(ipaddress.ip_network(cidr))

        return cidrs

    def get_known_cidrs(self):
        '''Return "known" CIDRs for this zone
        "known" CIDRs are meant to be CIDRs that you know about but that you
        don't own or control.'''
        return self._get_cidrs('known')

    def get_eligible_cidrs(self):
        '''For reasons lost in the dim reaches of time the system
        calls "Eligible" "Trusted" under the covers.  In any case
        it's the CIDRs that we're allowed to scan if we discover them'''
        return self._get_cidrs('trusted')

    def get_trusted_cidrs(self):
        '''For reasons lost in the dim reaches of time the system
        calls "Eligible" as "Trusted" under the covers.  These are the
        CIDRs that we're allowed to scan if we otherwise discover them.'''
        return self._get_cidrs('trusted')

    def get_internal_cidrs(self):
        '''Return "internal" CIDRs for this zone
        "internal" CIDRs are the ones you own or control that are part of
        your network'''
        return self._get_cidrs('internal')

    def get_avoid_cidrs(self):
        '''Return "avoid" CIDRs for this zone
        "avoid" CIDRs are the ones we won't actively scan
        '''
        return self._get_cidrs('avoid')

    def _set_cidrs(self, cidr_type, *cidrs, append=False, chunk_size=5000):
        if cidr_type not in ('known', 'trusted', 'internal', 'avoid'):
            raise spectreapi.InvalidArgument('%s is not a valid type for _set_cidrs')

        if self.server is None:
            raise spectreapi.NoServerException(
                'Collector.setCidrs() requires a Zone with a server')

        clist = []
        print(cidrs)
        for cidr in cidrs:
            if isinstance(cidr, list): # Okay, we're a list of CIDRs (hopefully)
                for c2 in cidr:
                    clist.append('{"address":"%s"}' % str(c2))
            else:
                clist.append('{"address":"%s"}' % str(cidr))

        for i in range( math.ceil( len(clist) / chunk_size)):

            data = '{"addresses":[' + ','.join(clist[i*chunk_size:(i+1)*chunk_size]) + ']}'
            params = {"append": str(append).lower()}

            results = self.server.post('zone/%d/cidr/%s' %
                                    (self.id_num, cidr_type), data=data, params=params)
            append = True # after the first chunk, append regardless

            if not results.ok:
                raise spectreapi.SpectreException(results.text)

        return results


    def _delete_cidrs(self, cidr_type, *cidrs, chunk_size=5000):
        if cidr_type not in ('known', 'trusted', 'internal', 'avoid'):
            raise spectreapi.InvalidArgument('%s is not a valid type for _set_cidrs')

        if self.server is None:
            raise spectreapi.NoServerException(
                'Collector.setCidrs() requires a Zone with a server')

        clist = []
        print(cidrs)
        for cidr in cidrs:
            if isinstance(cidr, list): # Okay, we're a list of CIDRs (hopefully)
                for c2 in cidr:
                    clist.append('{"address":"%s"}' % str(c2))
            else:
                clist.append('{"address":"%s"}' % str(cidr))

        for i in range( math.ceil( len(clist) / chunk_size)):

            data = '{"addresses":[' + ','.join(clist[i*chunk_size:(i+1)*chunk_size]) + ']}'

            results = self.server.delete('zone/%d/cidr/%s' %
                                    (self.id_num, cidr_type), data=data)

            if not results.ok:
                raise spectreapi.SpectreException(results.text)

        return results

    def set_known_cidrs(self, *cidrs, append=False, chunk_size=5000):
        '''Set "known" CIDRs for this zone.
        "known" CIDRs are meant to be CIDRs that you know about but that you
        don't own or control.'''
        return self._set_cidrs('known', *cidrs, append=append, chunk_size=chunk_size)

    def set_eligible_cidrs(self, *cidrs, append=False, chunk_size=5000):
        '''Set "eligible" CIDRs for this zone.
        These are the CIDRs we're allowed to scan if we learn about them'''
        return self._set_cidrs('trusted', *cidrs, append=append, chunk_size=chunk_size)

    def set_trusted_cidrs(self, *cidrs, append=False, chunk_size=5000):
        '''Set "trusted" (AKA "eligible") CIDRs for this zone.'''
        return self._set_cidrs('trusted', *cidrs, append=append, chunk_size=chunk_size)

    def set_internal_cidrs(self, *cidrs, append=False, chunk_size=5000):
        '''Set "internal" CIDRs for this zone.
        "internal" CIDRs are the ones you own or control that are a part of your network'''
        return self._set_cidrs('internal', *cidrs, append=append, chunk_size=chunk_size)

    def set_avoid_cidrs(self, *cidrs, append=False, chunk_size=5000):
        '''Set "avoid" CIDRs for this zone.
        "avoid" CIDRs are the ones we won't actively scan'''
        return self._set_cidrs('avoid', *cidrs, chunk_size=chunk_size)

    def delete_eligible_cidrs(self, *cidrs, chunk_size=5000):
        return self._delete_cidrs('trusted', *cidrs, chunk_size=chunk_size)

    def delete_trusted_cidrs(self, *cidrs, chunk_size=5000):
        return self._delete_cidrs('trusted', *cidrs, chunk_size=chunk_size)

    def delete_internal_cidrs(self, *cidrs, chunk_size=5000):
        return self._delete_cidrs('internal', *cidrs, chunk_size=chunk_size)

    def delete_avoid_cidrs(self, *cidrs, chunk_size=5000):
        return self._delete_cidrs('avoid', *cidrs, chunk_size=chunk_size)

    def delete_known_cidrs(self, *cidrs, chunk_size=5000):
        return self._delete_cidrs('known', *cidrs, chunk_size=chunk_size)

    def query(self, api='zonedata/devices'):
        return self.server.query(api).filter('zone.id', self.id_num)

    def get_or_create_collector(self,name):
        collector = self.server.get_collector_by_name(name)
        if collector:
            return collector

        data = '''
            [ {
                "@class" : "collector",
                "name" : "%s",
                "discoveryInterface" : {
                "name" : "%s:eth0",
                "type" : "ETHERNET",
                "active" : true,
                "config" : "manual/10000/full",
                "ospf" : { }
                },
                "zone" : {
                "id" : %d,
                "name" : "%s"
                },
                "enabled" : true,
                "rescanInterval" : 150,
                "hostDiscovery" : {
                    "enabled" : true,
                    "icmp" : true,
                    "dns" : false,
                    "snmp" : false,
                    "udp" : false
                }
                } ] ''' % (name, self.server.name, self.id_num, self.name)
        r = self.server.post("zone/collector", data=data);
        collector = self.server.get_collector_by_name(name)
        return collector


    def get_device_details_by_ip(self, ip):
        '''Return the details for one ore more devices for a zone with an address of <ip>
        This method returns all available details (minus the profile data prior to Spectre 3.3.1)'''
        params = {
            'filter.zone.id': self.id_num,
            'filter.address.ip' : ip,
            'detail.ScanType' : True,
            'detail.Attributes' : True,
            'detail.Protocol' : True,
            'detail.Port' : True,
            'detail.AlternateAddress' : True,
            #'detail.Profile' : True,
            #'detail.ProfileDetails' : True,
            'detail.ReferenceIp' : True,
            'detail.Details' : True,
            'detail.LeakResponse' : True,
            'detail.Certificate' : True,
            'detail.Interfaces' : True,
            'detail.Vlans' : True,
            'detail.Collector' : True,
            'detail.SnmpAlias' : True,
        }

        if LooseVersion(self.server.version) >= LooseVersion("3.3.1"):
            params['detail.Profile'] = True
            params['detail.ProfileDetails'] = True

        return self.server.get('zonedata/devices', params=params)
