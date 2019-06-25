def requestsHelper(func, headers={}, **parameters):
    headers['User-Agent']    = 'AIHUB Client 1.0'
    return resultHelper(func(headers=headers, **parameters))

def resultHelper(request_result):
    if request_result.status_code == 200:
         if request_result.headers.get('Content-Type') == "application/json":
            return request_result.json()
         else:
            return request_result.content
    else:
        if request_result.headers.get('Content-Type') == "application/json":
            exception = Exception(request_result.json()['message'])
            exception.status_code = request_result.status_code
            raise exception
    raise Exception('Something wrong. Please contact the system manager.')