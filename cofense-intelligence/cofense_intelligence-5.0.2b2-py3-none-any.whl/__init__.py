# -*- coding: utf-8 -*-
"""
Cofense Intelligence
~~~~~~~~~~~~~~~~~~~~

A library created by Cofense Intelligence to support developing integregations with client security architecture.

For more information on gaining access to Cofense Intelligence data at
https://phishme.com/product-services/phishing-intelligence

If you are already a customer, detailed documentation on the Intelligence API can be found at
https://www.threathq.com/documentation/display/MAD


The download and/or use of this Cofense application is subject to the terms and conditions set forth at https://phishme.com/legal/integration-applications/.

 Copyright 2013-2019 Cofense, Inc.  All rights reserved.

 This software is provided by PhishMe, Inc. ("Cofense") on an "as is" basis and any express or implied warranties,
 including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
 disclaimed in all aspects.  In no event will Cofense be liable for any direct, indirect, special, incidental or
 consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
 this software is pursuant to, and permitted only in accordance with, the agreement between you and Cofense.


Author: Cofense Intelligence Solutions Engineering
Support: support@cofense.com
"""

try:
    from .core import CFIntelSync
    from .output import CofenseIntegration, FileOutput, JsonFileOutput, CsvFileOutput, CefFileOutput, StixFileOutput
    from .intelligence import PhishThreatReport, MalwareThreatReport, ThreatReport
    from .api import IntelligenceAPI
    from .metadata import __version__

except:
    from .metadata import __version__
