"""
Brython Framework: Production views
===================================

"""


import json
import cgi

########################################################################
class BrythonView:
    """"""

    #----------------------------------------------------------------------
    def __new__(self, environ, start_response):
        """"""

        if not environ['REQUEST_METHOD'] == 'POST':
            return b'HOLALALLAL'


        if not environ['PATH_INFO'] == "/system_python":
            return b'incorrect_path'

        post_env = environ.copy()
        post_env['QUERY_STRING'] = ''
        post = cgi.FieldStorage(
            fp=environ['wsgi.input'],
            environ=post_env,
            keep_blank_values=True
        )

        name = post['name'].value
        args = eval(post['args'].value)
        kwargs = eval(post['kwargs'].value)


        if name:
            v = getattr(self, name)(self, *args, **kwargs)

            #if isinstance(v, dict):
                #return JsonResponse(v)
            #else:
            if v is None:
                data = json.dumps({'__RDNT__': 0,})
            #if v in [False, True]:
                #return JsonResponse({'__RDNT__': int(v),})
            else:
                data = json.dumps({'__RDNT__': v,})

        start_response('200 OK', [('Content-Type', 'aplication/json')])
        return [data.encode('utf-8')]



    #----------------------------------------------------------------------
    def test(self):
        """"""
        return True

