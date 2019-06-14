# -*- coding: utf-8 -*-

import os

config = {
    # Just for dev.
    "validate_signatures": False,

    # Talk to the relay, so things also make it to composer.stg in our dev env
    "active": True,

    # Since we're in active mode, we don't need to declare any of our own
    # passive endpoints.  This placeholder value needs to be here for the tests
    # to pass in Jenkins, though.  \o/
    "endpoints": {
        "fedora-infrastructure": [
            # Just listen to staging for now, not to production (spam!)
            # "tcp://hub.fedoraproject.org:9940",
            "tcp://stg.fedoraproject.org:9940",
        ],
    },
}

# developer's instance (docker/vagrant/...)
if 'ODCS_DEVELOPER_ENV' in os.environ and \
   os.environ['ODCS_DEVELOPER_ENV'].lower() in (
       '1', 'on', 'true', 'y', 'yes'):
    config['endpoints']['relay_outbound'] = ["tcp://fedmsg-relay:2001"]
    config['relay_inbound'] = ["tcp://fedmsg-relay:2003"]
else:
    # These configuration values are reasonable for most other configurations.
    config['endpoints']['relay_outbound'] = ["tcp://127.0.0.1:4001"]
    config['relay_inbound'] = ["tcp://127.0.0.1:2003"]
