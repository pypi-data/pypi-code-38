# encoding: utf-8

import sys
import pcapy
import logging_helper
from networkutil.interfaces import get_interface_names

logging = logging_helper.setup_logging()


def get_live_interfaces():
    # Grab a list of interfaces that pcap is able to listen on.
    # The current user will be able to listen from all returned interfaces,
    # using open_live to open them.
    ifs = pcapy.findalldevs()

    # No interfaces available, abort.
    if 0 == len(ifs):
        logging.info(u"You don't have permissions to open any interface on this system.")
        sys.exit(1)

    return ifs


def get_live_named_interfaces():

    ifs = get_live_interfaces()

    # Process the list depending on OS to get interface names (best effort)
    interface_names = get_interface_names()

    for i in range(len(ifs)):
        try:
            # Perform best effort update for each interface!
            ifs_name = interface_names[ifs[i].replace(u'\\Device\\NPF_', u'')]

        except KeyError:
            ifs_name = u'Unknown'

        ifs[i] = (ifs[i], ifs_name)

    return ifs
