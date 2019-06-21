from connection import api_get


def get_app_url(app):
    return api_get('/app/url?name={0}'.format(app))

def get_device_domain_name():
    return api_get('/app/device_domain_name')

def get_app_domain_name(app):
    return api_get('/app/domain_name?name={0}'.format(app))
