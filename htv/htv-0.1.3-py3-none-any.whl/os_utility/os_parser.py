#################################################
#            Get PARAMETERS IDs or names        #
#################################################

# Images
def get_images(doc):
    # It creates the empty list 'image'
    images = []
    # We store our 'doc' in the 'image_dict' variable
    image_dict = doc['resources']
    # It iterates image_dict dictionary items
    for key, value in image_dict.items():
        # If our item key has a key "properties" it will iterate that dictionary looking for the 'image' key
        if "properties" in image_dict[key]:
            prop = image_dict[key]['properties']
            for k, v in prop.items():
                # If there is a key called "image" it will save its value to the list "images"
                if k == "image":
                    images.append(v)
    return images

# Flavors
def get_flavors(doc):
    # It creates the empty list 'flavor'
    flavors = []
    # We store our 'doc' in the 'flavor_dict' variable
    flavor_dict = doc['resources']
    for key, value in flavor_dict.items():
        # If our item key has a key "properties" it will iterate that dictionary looking for the 'flavor' key
        if "properties" in flavor_dict[key]:
            prop = flavor_dict[key]['properties']
            for k, v in prop.items():
                # If there is a key called "flavor" it will save its value to the list "flavors"
                if k == "flavor":
                    flavors.append(v)
    return flavors

# Security groups
def get_secgroups(doc):
    # It creates the empty list 'sec_groups'
    sec_groups = []
    # We store our 'doc' in the "sec_groups_dict" variable
    sec_groups_dict = doc['resources']
    for key, value in sec_groups_dict.items():
        # If our key has a key "properties" it'll iterate that dictionary looking for the 'security_groups' key
        if "properties" in sec_groups_dict[key]:
            prop = sec_groups_dict[key]['properties']
            for k, v in prop.items():
                # If there is a key called "security_groups" it will save its value to the list "sec_groups"
                if k == "security_groups":
                    sec_groups.append(v[0])
    return sec_groups

# Networks
def get_networks(doc):
    # It creates the empty list 'network'
    networks = []
    # We store our 'doc' in the "network_dict" variable
    network_dict = doc['resources']
    # It iterates inside our network_dict dictionary items
    for key, value in network_dict.items():
        # If our item key has a key "properties" it will iterate that dictionary looking for the 'network' key
        if "properties" in network_dict[key]:
            prop = network_dict[key]['properties']
            for k, v in prop.items():
                # If there is a key called "network" it will save its value to the list "networks"
                if k == "networks":
                    networks.append(v)
                elif k == "network":
                    networks.append(v)
    return networks

# Ports
def get_ports(doc):
    # It creates the empty list 'port'
    ports = []
    # We store our 'doc' in the "port_dict" variable
    port_dict = doc['resources']
    # It iterates inside our port_dict dictionary items
    for key, value in port_dict.items():
        # If our item key has a key "properties" it will iterate that dictionary looking for the 'port' key
        if "properties" in port_dict[key]:
            prop = port_dict[key]['properties']
            for k, v in prop.items():
                # If there is a key called "port" it will save its value to the list "ports"
                if k == "port_id" or k == "port":
                    ports.append(v)
    return ports

# Keypairs
def get_keypairs(doc):
    # It creates the empty list 'keypairs'
    keypairs = []
    # We store our 'doc' in the "keypair_dict" variable
    keypair_dict = doc['resources']
    # It iterates inside our keypair_dict dictionary items
    for key, value in keypair_dict.items():
        # If our item key has a key "properties" it will iterate that dictionary looking for the 'keypair' key
        if "properties" in keypair_dict[key]:
            prop = keypair_dict[key]['properties']
            for k, v in prop.items():
                # If there is a key called "keypair" it will save its value to the list "keypairs"
                if k == "key_name":
                    keypairs.append(v)
    return keypairs

# Volumes
def get_volumes(doc):
    # It creates the empty list 'volumes'
    volumes = []
    # We store our 'doc' in the "volume_dict" variable
    volume_dict = doc['resources']
    # It iterates inside our volume_dict dictionary items
    for key, value in volume_dict.items():
        # If our item key has a key "properties" it will iterate that dictionary looking for the 'volume' key
        if "properties" in volume_dict[key]:
            prop = volume_dict[key]['properties']
            for k, v in prop.items():
                # If there is a key called "volume" it will save its value to the list "volumes"
                if k == "volume":
                    volumes.append(v)
    return volumes
