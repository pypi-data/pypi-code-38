# -*- coding: utf-8 -*-
"""Init and utils."""
from zope.i18nmessageid import MessageFactory

import logging


PROJECTNAME = 'collective.getfeed'
_ = MessageFactory(PROJECTNAME)
logger = logging.getLogger(PROJECTNAME)
