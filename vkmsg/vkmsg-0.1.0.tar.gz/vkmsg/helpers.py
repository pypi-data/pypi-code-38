from urllib.parse import quote_plus


def get_query_string(**kwargs):
    res = []
    for key in kwargs:
        r = f'{key}={quote_plus(str(kwargs[key]))}&'
        res.append(r)

    return ('?' + ''.join(res)).replace('+', '%20')
