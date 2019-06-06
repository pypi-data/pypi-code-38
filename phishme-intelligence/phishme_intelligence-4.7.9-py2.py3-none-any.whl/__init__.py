# -*- coding: utf-8 -*-
"""
PhishMe Intelligence
~~~~~~~~~~~~~~~~~~~~

A library created by PhishMe Intelligence to support developing integregations with client security architecture.

For more information on gaining access to PhishMe Intelligence data at
https://phishme.com/product-services/phishing-intelligence

If you are already a customer, detailed documentation on the Intelligence API can be found at
https://www.threathq.com/documentation/display/MAD


The download and/or use of this PhishMe application is subject to the terms and conditions set forth at https://phishme.com/legal/integration-applications/.

Copyright 2013-2017 PhishMe, Inc.  All rights reserved.

This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.

Author: PhishMe Intelligence Solutions Engineering
Support: support@phishme.com
"""

# This funkiness allows us to use metadata for version number in the setup script.
try:
    import requests

    from .core.exceptions import PmNotImplemented, PmSyncError, PmValidationError, PmAttributeError, \
        PmBadConnectionType, PmConnectionError, PmFileError, PmSearchTermError, PhishMeException
    from .core.phishme import PhishMeIntelligence, read_args, read_config
    from .core.rest_api import RestApi
    from .core.intelligence import Malware, IPv4, URL
    from .core.brand_intelligence import Phish
    from .output.base_integration import BaseIntegration
    from .output.generic.generic_integration import GenericIntegration
    from .output.generic.pm_cef import PmCef
    from .output.generic.pm_json import PmJson
    from .output.generic.pm_stix import PmStix
    from .core.metadata import __version__

except:
    from .core.metadata import __version__




