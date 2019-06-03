from django.conf import settings


def find_tuple_values(tpl, values):
    """
    Allow to find a key which is related to a value in python tuple
    """
    return [str(obj[0]) for obj in tpl if obj[1] in values]


def get_db_credentials():
    credentials = settings.DATABASES.get('default', None)
    result = None

    if credentials:
        result = {
            'HOST': credentials.get('HOST', ''),
            'USER': credentials.get('USER', ''),
            'PASS': credentials.get('PASSWORD', ''),
            'NAME': credentials.get('NAME', ''),
            'PORT': credentials.get('PORT', ''),
        }

    return result
