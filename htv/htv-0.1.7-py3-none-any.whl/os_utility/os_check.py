# Utilities imports
from htvalidator.os_utility.os_parser import get_images, get_flavors, get_secgroups, get_networks, get_ports, \
    get_keypairs, \
    get_volumes
from htvalidator.os_utility.os_verify import verify_images, verify_secgroups, verify_flavors, verify_networks, \
    verify_ports, \
    verify_keypairs, verify_volumes


#################################################
#             Check openstack items             #
#################################################
def check_openstack(doc, yamlfile, clients):
    images = []
    flavors = []
    sec_groups = []
    networks = []
    ports = []
    volumes = []
    keypairs = []
    # Glance: image
    try:
        images = get_images(doc)
    except Exception as e:
        print(e)
    # If the images list is populated it will try to look for the items inside the openstack items
    if images:
        try:
            verify_images(images, doc, yamlfile, clients)
        except Exception as e:
            print(e)

    # Nova: flavor
    try:
        flavors = get_flavors(doc)
    except Exception as e:
        print(e)
    # If the flavors list is populated it will try to look for the items inside the openstack items
    if flavors:
        try:
            verify_flavors(flavors, doc, yamlfile, clients)
        except Exception as e:
            print(e)

    # Neutron: security group
    try:
        sec_groups = get_secgroups(doc)
    except Exception as e:
        print(e)
    # If the sec_groups list is populated it will try to look for the items inside the openstack items
    if sec_groups:
        try:
            verify_secgroups(sec_groups, doc, yamlfile, clients)
        except Exception as e:
            print(e)

    # Neutron: networks
    try:
        networks = get_networks(doc)
    except Exception as e:
        print(e)
    # If the networks list is populated it will try to look for the items inside the openstack items
    if networks:
        try:
            verify_networks(networks, doc, yamlfile, clients)
        except Exception as e:
            print(e)

    # Neutron: ports
    try:
        ports = get_ports(doc)
    except Exception as e:
        print(e)
    # If the ports list is populated it will try to look for the items inside the openstack items
    if ports:
        try:
            verify_ports(ports, doc, yamlfile, clients)
        except Exception as e:
            print(e)

    # Nova: key pairs
    try:
        keypairs = get_keypairs(doc)
    except Exception as e:
        print(e)
    # If the ports list is populated it will try to look for the items inside the openstack items
    if keypairs:
        try:
            verify_keypairs(keypairs, doc, yamlfile, clients)
        except Exception as e:
            print(e)

    # Cinder: volumes
    try:
        volumes = get_volumes(doc)
    except Exception as e:
        print(e)
    # If the ports list is populated it will try to look for the items inside the openstack items
    if volumes:
        try:
            verify_volumes(volumes, doc, yamlfile, clients)
        except Exception as e:
            print(e)
