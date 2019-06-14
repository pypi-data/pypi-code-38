from omero_mapr.utils.version import get_version


def mapr_url_suffix(request):
    suffix = u"?_%s" % get_version()
    return {'mapr_url_suffix': suffix}
