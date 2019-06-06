# -*- coding: utf-8 -*-
#
# name:             record.py
# author:           Harold Bradley III | Prestix Studio, LLC.
# email:            harold@prestix.studio
# created on:       09/15/2018
#

"""
cloudns_api.record
~~~~~~~~~~~~~~~~~~

This module contains API wrapper functions for DNS listing, creating, updating,
and deleting records.

There are also a functions for activating/deactivating a record, importing
records, copying existing records

For SOA records, see soa.py
"""

import requests

from .api import api, patch_update
from .parameters import Parameters


@api
def get(domain_name=None, record_id=None):
    # TODO: will have to list, then loop and try to get record_id
    pass


@api
def list(domain_name=None, host='', record_type=''):
    """Lists DNS records for a particular domain.

    :param domain_name: string, the domain name for which to retrieve the
        records
    :param host: (optional) string, a host to limit results by. Use '@' for
        domain as host.
    :param record_type: (optional) string, the record type to retrieve (ie,
        'a', 'cname', etc..., See RECORD_TYPES)
    """
    url = 'https://api.cloudns.net/dns/records.json'

    params = Parameters({
            'domain-name': domain_name,
            'host': {
                'value': host,
                'optional': True
            },
            'type': {
                'value': type,
                'optional': True
            },
        })

    return requests.get(url, params=params.to_dict())


def _get_record_parameters(domain_name=None, record_type=None, host=None,
                           record=None, ttl=None, priority=None, weight=None,
                           port=None, frame=None, frame_title='',
                           frame_keywords='', frame_description='',
                           save_path=None, redirect_type=None, mail=None,
                           txt=None, algorithm=None, fptype=None, status=1,
                           geodns_location=None, caa_flag=None, caa_type='',
                           caa_value=''):
    """Creates and returns create/update DNS record Parameters object.

    This helps to avoid code duplication.

    :param domain_name: string, (required) the domain name for which to
        retrieve the records
    :param record_type: string, (required) the record type to retrieve (ie,
        'a', 'cname', etc..., See RECORD_TYPES)
    :param host: string, (required) the host for this record. Use '@' for
        domain as host.
    :param record: string, (required) the record to be added
    :param ttl: int, (required) the time-to-live for this record
    :param priority: (optional) int, used for MX or SRV records
    :param weight: (optional) int, weight for SRV record
    :param port: (optional) int, port for SRV record
    :param frame: (optional) int, 0 or 1 for Web redirects to disable or enable
        frame
    :param frame_title: (optional) string, title if frame is enabled in Web
        redirects
    :param frame_keywords: (optional) string, keywords if frame is enabled in
        Web redirects
    :param frame_description: (optional) string, description if frame is
        enabled in Web redirects
    :param save_path: (optional) int, 0 or 1 for Web redirects
    :param redirect_type: (optional) int, 301 or 302 for Web redirects if frame
        is disabled
    :param mail: (optional) int?, e-mail address for RP records
    :param txt: (optional) int?, domain name for TXT record used in RP records
    :param algorithm: (required only for SSHFP) int, algorithm used to create
        the SSHFP fingerprint. Required for SSHFP records only.
    :param fptype: (required only for SSHFP) int, type of the SSHFP algorithm.
        Required for SSHFP records only.
    :param status: (optional) int, set to 1 to create the record active or to 0
        to create it inactive. If omitted the record will be created active.
    :param geodns_location: (optional) int, ID of a GeoDNS location for A, AAAA
        or CNAME record. The GeoDNS locations can be obtained with List GeoDNS
        locations
    :param caa_flag: (optional) int, 0 - Non critical or 128 - Critical
    :param caa_type: (optional) string, type of CAA record. The available flags
        are issue, issuewild, iodef.
    :param caa_value: (optional) string, if caa_type is issue, caa_value can be
        hostname or ";". If caa_type is issuewild, it can be hostname or ";".
        If caa_type is iodef, it can be "mailto:someemail@address.tld,
        http://example.tld or http://example.tld.
    """
    param_args = {
            'domain-name': domain_name,
            'host': host,
            'ttl': ttl,
            'record': {
                'value': admin_mail,
                'optional': record_type in ['RP', 'CAA'],
            },
            'priority': {
                'value': priority,
                'optional': record_type not in ['MX', 'SRV'],
            },
            'weight': {
                'value': weight,
                'optional': record_type != 'MX',
            }, # TODO: what happens if I pass a value when this is not needed?
            'port': {
                'value': port,
                'optional': record_type != 'SRV',
            },
            'frame': {
                'value': frame,
                'optional': record_type != 'WR',
            },
            'frame-title': {
                'value': frame_title,
                'optional': True,
            },
            'frame-keywords': {
                'value': frame_keywords,
                'optional': True,
            },
            'frame-description': {
                'value': frame_description,
                'optional': True,
            },
            'save-path': {
                'value': save_path,
                'optional': True,
            },
            'redirect-type': {
                'value': redirect_type,
                'optional': record_type != 'WR',
            },
            'mail': {
                'value': mail,
                'optional': True,
            },
            'txt': {
                'value': mail,
                'optional': record_type != 'RP', # TODO: I think this is correct
            },
            'algorithm': {
                'value': algorithm,
                'optional': record_type != 'SSHFP',
            },
            'fptype': {
                'value': fptype,
                'optional': record_type != 'SSHFP',
            },
            'status': {
                'value': status,
                'optional': True,
            },
            'geodns-location': {
                'value': geodns_location,
                'optional': True,
            },
            'caa-flag': {
                'value': caa_flag,
                'optional': True,
            },
            'caa-type': {
                'value': caa_type,
                'optional': True,
            },
            'caa-value': {
                'value': caa_value,
                'optional': True,
            },
            'expire': {
                'value': expire,
                'min_value': 1209600,
                'max_value': 2419200,
            },
            'default-ttl': {
                'value': default_ttl,
                'min_value': 60,
                'max_value': 2419200,
            },
        }

    if 'record_type' in kwargs:
        param_args['record-type'] = kwargs['record_type']
        # TODO: type vs record-type (should be fine now?)
        # TODO: may not work with update since this is not required or
        # wanted.

    if 'record_id' in kwargs:
        param_args['record-id'] = kwargs['record_id']
        # TODO: type vs record-type (should be fine now?)
        # TODO: may not work with update since this is not required or
        # wanted.

    return Parameters(param_args)


@api
def create(domain_name=None, record_type=None, **kwargs):
    """Creates a DNS record.

    :param domain_name: string, (required) the domain name for which to
        retrieve the records
    """
    url = 'https://api.cloudns.net/dns/add-record.json'

    if 'record_id' in kwargs:
        # TODO: test
        raise Exception('cant do this...')

    params = _get_record_parameters(domain_name, record_type, **kwargs)

    return requests.post(url, params=params.to_dict())


@api
@patch_update(get=get, keys=['domain_name'])
def update(domain_name=None, record_id=None, patch=False, **kwargs):
    """Updates a DNS record.

    :param domain_name: string, (required) the domain name for which to
        retrieve the records
    :param record_id: int, (required) the record id for the record to update
    :param patch: boolean, whether or not to do a patch update
    """
    url = 'https://api.cloudns.net/dns/mod-record.json'

    if 'record_type' in kwargs:
        # TODO: test
        raise Exception('cant do this...')

    params = _get_record_parameters(domain_name, record_id, **kwargs)

    return requests.post(url, params=params.to_dict())


def patch(*args, **kwargs):
    """A convenience function for patch updates."""
    return update(*args, patch=True, **kwargs)


@api
def delete(page=1, rows_per_page=30, search=''):
    """Deletes a DNS record

    :param page: (optional) int, current page
    :param rows_per_page: (optional) int, number of results on each page
    :param search: (optional) string used to search domain names, reverse zone
        name, or other keyword to search for in the zone names
    """

    params['page'] = page


@api
def transfer(domain_name, record_id):
    """Toggles active/inactive status on a particular record of a domain name.

    :param domain_name: string, the domain name on which to work
    :param record_id: int, record id (the id returned when listing records)
    """
    params['domain_name'] = domain_name
    params['record_id'] = record_id

    return post(url, params=params)


@api
def toggle_activation(domain_name, record_id):
    """Toggles active/inactive status on a particular record of a domain name.

    :param domain_name: string, the domain name on which to work
    :param record_id: int, record id (the id returned when listing records)
    """
    params['domain_name'] = domain_name
    params['record_id'] = record_id

    return post(url, params=params)


@api
def activate(domain_name, record_id):
    """Makes a particular record on a domain name active

    :param domain_name: string, the domain name on which to work
    :param record_id: int, record id (the id returned when listing records)
    """
    params['domain_name'] = domain_name
    params['record_id'] = record_id
    params['status'] = 1

    return post(url, params=params)


@api
def deactivate(domain_name, record_id):
    """Makes a particular record on a domain name inactive

    :param domain_name: string, the domain name on which to work
    :param record_id: int, record id (the id returned when listing records)
    """

    url = 'https://api.cloudns.net/dns/change-record-status.json'

    params['domain_name'] = domain_name
    params['record_id'] = record_id
    params['status'] = 2

    return post(url, params=params)
