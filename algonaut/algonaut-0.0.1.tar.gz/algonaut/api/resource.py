from flask import jsonify, request, Response, make_response
from flask.views import View
import traceback
import time
import werkzeug
import re
import hashlib
import logging

from algonaut.settings import settings

logger = logging.getLogger(__name__)

class NotModified(werkzeug.exceptions.HTTPException):

    code = 304

    def get_response(self, environment):
        return Response(status=304)

class classproperty(property):

    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner )()

class Resource(View):

    export_map = {}

    @classmethod
    def export(cls,obj):
        raise NotImplementedError

    def dispatch_request(self,*args,**kwargs):
        return self.handle(request.method,*args,**kwargs)

    def make_response(self,data):
        if isinstance(data,str) or isinstance(data,str) or isinstance(data,Response):
            return data
        return jsonify(data)

    @classproperty
    def export_fields(self):
        export_fields = [field for field in self.export_map
                         if isinstance(field,str)] + \
                        [subfield for field in self.export_map
                         if isinstance(field,dict)
                         for subfield in field.keys()]
        return export_fields

    @property
    def language(self):
        return 'en'

    def t(self, key, *args, **kwargs):
        return settings.translate(self.language, key, *args, **kwargs)

    def add_cache_headers(self,response):
        digest = hashlib.sha1()
        digest.update(response.get_data())
        hexdigest = digest.hexdigest()
        if 'if-none-match' in request.headers:
            etag = request.headers['if-none-match']
            # remove quotation marks if present
            if etag[0] == '"' and etag[-1] == '"':
                etag = etag[1:-1]
            # Apache adds a "-gzip" suffix, if it compressed
            # the JSON on the fly; strip this suffix if it exists
            if etag[-5:] == "-gzip":
                etag = etag[:-5]
            if etag == hexdigest:
                raise NotModified

        h = response.headers
        h['Cache-Control'] = 'private, no-cache, must-revalidate, max-age=0, post-check=0, pre-check=0'
        h['Expires'] = 'Thu, 01 Dec 1994 16:00:00 GMT' # definitely in the past => no caching
        response.set_etag(str(hexdigest))
        return response

    def add_crossdomain_headers(self, response):

        opts = settings.get('crossdomain')
        if not opts or not opts.get('enabled', False):
            return

        def origin_allowed(origin, allowed_origins):
            for allowed_origin in allowed_origins:
                if re.match(allowed_origin, origin):
                    return True
            return False

        origin = request.headers.get('Origin')

        if not origin or not origin_allowed(origin, opts.get('origins', [])):
            return

        #we add cross-domain headers
        response.headers['Access-Control-Allow-Origin'] = origin
        #we allow all methods that are defined in the class
        response.headers['Access-Control-Allow-Methods'] = ", ".join([method for method in ('GET', 'POST', 'PUT', 'PATCH', 'DELETE') if hasattr(self, method.lower())])
        response.headers['Access-Control-Max-Age'] = str(opts.get('max-age', 120))
        response.headers['Access-Control-Allow-Headers'] = request.headers.get('Access-Control-Request-Headers', ', '.join(opts.get('allowed-headers', [])))

    def handle(self,method,*args,**kwargs):

        request.originating_ip = request.headers.get('X-Client-IP',
            request.headers.get('X-Originating-IP', request.remote_addr))
        request.anon_ip = '.'.join(request.originating_ip.split('.')[:-1]+['0'])

        _do_profile = 1
        start = time.time()
        if method.lower() == 'options':
            response = make_response('')
            status_code = 200
        elif not hasattr(self,method.lower()):
            response = self.make_response({'message' : 'Method forbidden'})
            status_code = 405
            return response, status_code
        else:
            handler = getattr(self,method.lower())
            try:
                handler_response = handler(*args,**kwargs)
                if isinstance(handler_response,(tuple,list)):
                    data,status_code =  handler_response
                    response = self.make_response(data)
                else:
                    response = handler_response
                    status_code = response.status_code
            except TypeError as e:
                response = self.make_response({'message' : 'An unknown error occured'})
                logger.error(traceback.format_exc())
                status_code = 403
            except BaseException as e:
                response = self.make_response({'message' : 'Internal server error'})
                logger.error(traceback.format_exc())
                status_code = 500

        response.headers.add('X-elapsed-time-ms',str("%d" % int((time.time()-start)*1000)))
        self.add_crossdomain_headers(response)
        return self.add_cache_headers(response), status_code
