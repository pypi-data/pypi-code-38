from connection import api_post, api_get


def init_storage(app, user):
    return api_post('/app/init_storage', data={"app_name": app, "user_name": user})


def get_storage_dir(app):
    return api_get('/app/storage_dir?name={0}'.format(app))
