from connection import api_post


def restart(service_name):
    return api_post('/service/restart', data={"name": service_name})

