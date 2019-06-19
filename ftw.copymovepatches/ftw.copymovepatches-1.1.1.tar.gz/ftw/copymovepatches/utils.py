import pkg_resources

IS_PLONE_5 = pkg_resources.get_distribution('Products.CMFPlone').version >= '5'

try:
    # CMFCore >= 2.2.11
    from Products.CMFCore.indexing import getQueue
except ImportError:
    try:
        from collective.indexing.queue import getQueue
    except ImportError:
        getQueue = None

try:
    pkg_resources.get_distribution('collective.indexing')
except pkg_resources.DistributionNotFound:
    HAS_C_INDEXING = False
else:
    HAS_C_INDEXING = True
