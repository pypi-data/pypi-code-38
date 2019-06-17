"""
@author: Julian Sobott
@created: 13.11.2018
@brief:
@description:

@external_use:

@internal_use:

"""
import logging


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(levelname)-8s %(message)s \t\t(%(filename)s %(lineno)d) \t%(msecs).5s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


