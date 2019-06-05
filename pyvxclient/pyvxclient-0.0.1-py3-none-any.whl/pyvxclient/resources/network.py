import logging
from pyvxclient.decorators import paginate


class Network(object):
    def __init__(self, client, logger=None):
        self.log = logger if logger else logging.getLogger(__name__)
        self.client = client

    """
      id (string, optional),
      ip_address (string, optional),
      ip_subnet (string, optional),
      lease (string, optional),
      mac (string, optional),
      network_operator (string, optional),
      object (string, optional),
      object_group (string, optional),
      object_number (string, optional),
      service_provider (string, optional),
      updated (string, optional),
      vlan (string, optional),
      vlan_id (string, optional)
    """

    @paginate
    def GetIPAddress(self, limit=10, sort=["id"], q=[], fields=[], page=None):
        return self.client.network.getIpAddress(per_page=limit, sort=sort, q=q, fields=fields,
                                                page=page).response().result

    """
      active_ips (string, optional),
      created (string, optional),
      dns1 (string, optional),
      dns2 (string, optional),
      domain (string, optional),
      gateway (string, optional),
      id (string, optional),
      name (string, optional),
      netmask (string, optional),
      network (string, optional),
      number_ips (string, optional),
      reclaim (string, optional),
      service_provider (string, optional),
      status (string, optional),
      type (string, optional),
      updated (string, optional),
      used_ips (string, optional),
      vlan (string, optional)
    """

    @paginate
    def GetIPSubnet(self, limit=10, sort=["id"], q=[], fields=[], page=None):
        return self.client.network.getIpSubnet(per_page=limit, sort=sort, q=q, fields=fields,
                                               page=page).response().result

    @paginate
    def GetNetwork(self, limit=10, sort=["id"], q=[], fields=[], page=None):
        return self.client.network.get_network(per_page=limit, sort=sort, q=q, fields=fields,
                                               page=page).response().result

    @paginate
    def GetInterface(self, limit=10, sort=["id"], q=[], fields=[], page=None):
        return self.client.network.getNetworkInterface(per_page=limit, sort=sort, q=q, fields=fields,
                                                       page=page).response().result

    @paginate
    def GetNode(self, limit=10, sort=["id"], q=[], fields=[], page=None):
        return self.client.network.get_network_node(per_page=limit, sort=sort, q=q, fields=fields,
                                                    page=page).response().result

    """
      id (string, optional),
      service_provider (string, optional),
      type (string, optional),
      vlan_id (string, optional),
      vlan_type (string, optional)  
      """

    @paginate
    def GetVLAN(self, limit=10, sort=["id"], q=[], fields=[], page=None):
        return self.client.network.get_network_vlan(per_page=limit, sort=sort, q=q, fields=fields,
                                                    page=page).response().result

    """
      created (string, optional),
      created_by (string, optional),
      id (string, optional),
      name (string, optional),
      type (string, optional) = ['u'untagged',u'tagged''],
      updated (string, optional),
      updated_by (string, optional)
    """

    @paginate
    def GetVLANType(self, limit=10, sort=["id"], q=[], fields=[], page=None):
        return self.client.network.getNetworkVlanType(per_page=limit, sort=sort, q=q, fields=fields,
                                                      page=page).response().result

    """
    created (string, optional),
    id (string, optional),
    module_number (string, optional),
    module_offset (string, optional),
    network (string, optional),
    network_operator (string, optional),
    number (string, optional),
    site (string, optional),
    status (string, optional) = ['u'Active',u'Broken',u'Reserved''],
    switch (string, optional),
    switch_name (string, optional),
    type (string, optional),
    updated (string, optional)
    """

    @paginate
    def GetPort(self, limit=10, sort=["id"], q=[], fields=[], page=None):
        return self.client.network.get_port(per_page=limit, sort=sort, q=q, fields=fields, page=page).response().result

    """
    errors (string, optional),
    id (string, optional),
    last_seen (string, optional),
    network (string, optional),
    network_operator (string, optional),
    occurrences (string, optional),
    port (string, optional),
    port_name (string, optional),
    remote (string, optional),
    switch (string, optional),
    switch_name (string, optional),
    updated (string, optional)
    """

    @paginate
    def GetPortError(self, limit=10, sort=["id"], q=[], fields=[], page=None):
        return self.client.network.get_port_error(per_page=limit, sort=sort, q=q, fields=fields,
                                                  page=page).response().result

    """
    created (string, optional),
    down_objects (string, optional),
    duration (string, optional),
    id (string, optional),
    include (string, optional),
    network (string, optional),
    network_operator (string, optional),
    note (string, optional),
    start (string, optional),
    stop (string, optional),
    switch (string, optional),
    switch_name (string, optional),
    updated (string, optional)
    """

    @paginate
    def GetServiceDisruption(self, limit=10, sort=["id"], q=[], fields=[], page=None):
        return self.client.network.getServiceDisruption(per_page=limit, sort=sort, q=q, fields=fields,
                                                        page=page).response().result

    """
    created (string, optional),
    description (string, optional),
    id (string, optional),
    latitude (string, optional),
    longitude (string, optional),
    name (string, optional),
    note (string, optional),
    postal_code (string, optional),
    street (string, optional),
    street_number (string, optional),
    updated (string, optional)
    """

    @paginate
    def GetSite(self, limit=10, sort=["id"], q=[], fields=[], page=None):
        return self.client.network.getSite(per_page=limit, sort=sort, q=q, fields=fields, page=page).response().result

    """
    active_ports (string, optional),
    address (string, optional),
    created (string, optional),
    down_since (string, optional),
    down_users (string, optional),
    driver (string, optional),
    id (string, optional),
    model (string, optional),
    name (string, optional),
    network (string, optional),
    network_operator (string, optional),
    number_of_ports (string, optional),
    parent1 (string, optional),
    parent2 (string, optional),
    peripheral (string, optional),
    site (string, optional),
    status (string, optional) = ['u'Active',u'Inactive''],
    updated (string, optional)  
    """

    @paginate
    def GetSwitch(self, limit=10, sort=["id"], q=[], fields=[], page=None):
        return self.client.network.get_switch(per_page=limit, sort=sort, q=q, fields=fields,
                                              page=page).response().result

    def Create(self):
        raise NotImplementedError

    def Update(self):
        raise NotImplementedError
