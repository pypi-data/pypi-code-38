from connection import api_get


def get_app_dir(app):
    return api_get('/app/install_path?name={0}'.format(app))


def get_data_dir(app):
    return api_get('/app/data_path?name={0}'.format(app))
