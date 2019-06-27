from http import HTTPStatus

from django.http import JsonResponse


class Problem(Exception):
    def __init__(self, title, status, detail, should_log=False):
        self.title = title
        self.status = status
        self.detail = detail
        self.should_log = should_log

    def to_response(self):
        resp = JsonResponse({'title': self.title,
                             'status': self.status,
                             'detail': self.detail})
        resp.status_code = self.status
        return resp

    # 4XX ---------------------------------------------------------------------
    def bad_request(detail="bad request"):
        return Problem('Bad Request', HTTPStatus.BAD_REQUEST, detail)

    def not_found(detail="not found"):
        return Problem('Not Found', HTTPStatus.NOT_FOUND, detail)

    def method_not_allowed():
        return Problem('Method not Allowed',
                       HTTPStatus.METHOD_NOT_ALLOWED,
                       ("The requested method is not available on "
                        "this resource"))

    def not_acceptable():
        return Problem('Not Acceptable',
                       HTTPStatus.NOT_ACCEPTABLE,
                       ("The requested resource is not capable of generating "
                        "content acceptable according to the Accept headers"))

    def unsupported_media_type(detail="unsupported media type"):
        return Problem('Unsupported Media Type',
                       HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                       detail)

    # 5XX ---------------------------------------------------------------------
    def internal_error(detail="internal error"):
        return Problem('Internal Error',
                       HTTPStatus.INTERNAL_SERVER_ERROR,
                       detail,
                       should_log=True)

    def bad_gateway(detail="bad gateway"):
        return Problem('Bad Gateway',
                       HTTPStatus.BAD_GATEWAY,
                       detail,
                       should_log=True)
