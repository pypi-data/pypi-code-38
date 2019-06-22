from connection import api_get


def get_email():
    return api_get('/user/email')
