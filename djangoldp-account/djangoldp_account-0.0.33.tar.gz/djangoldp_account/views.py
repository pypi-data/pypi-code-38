from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views import View

from djangoldp_account.endpoints.rp_login import RPLoginCallBackEndpoint, RPLoginEndpoint
from djangoldp_account.endpoints.webfinger import WebFingerEndpoint
from djangoldp_account.errors import LDPLoginError, WebFingerError
from oidc_provider.views import userinfo


def userinfocustom(request, *args, **kwargs):
    if request.method == 'OPTIONS':
        response = HttpResponse({}, status=200)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Headers'] = 'Authorization'
        response['Cache-Control'] = 'no-store'
        response['Pragma'] = 'no-cache'

        return response

    return userinfo(request, *args, **kwargs)


class RPLoginView(View):
    """
    RP authentication workflow
    See https://github.com/solid/webid-oidc-spec/blob/master/example-workflow.md
    Wa're using oid module : https://pyoidc.readthedocs.io/en/latest/examples/rp.html
    """
    endpoint_class = RPLoginEndpoint

    def get(self, request, *args, **kwargs):
        return self.on_request(request)

    def on_request(self, request):
        endpoint = self.endpoint_class(request)
        try:
            endpoint.validate_params()

            return HttpResponseRedirect(endpoint.op_login_url())

        except LDPLoginError as error:
            return JsonResponse(error.create_dict(), status=400)

    def post(self, request, *args, **kwargs):
        return self.on_request(request)


class RPLoginCallBackView(View):
    endpoint_class = RPLoginCallBackEndpoint

    def get(self, request, *args, **kwargs):
        return self.on_request(request)

    def on_request(self, request):
        endpoint = self.endpoint_class(request)
        try:
            endpoint.validate_params()

            return HttpResponseRedirect(endpoint.initial_url())

        except LDPLoginError as error:
            return JsonResponse(error.create_dict(), status=400)

    def post(self, request, *args, **kwargs):
        return self.on_request(request)


class WebFingerView(View):
    endpoint_class = WebFingerEndpoint

    def get(self, request, *args, **kwargs):
        return self.on_request(request)

    def on_request(self, request):
        endpoint = self.endpoint_class(request)
        try:
            endpoint.validate_params()

            return JsonResponse(endpoint.response())

        except WebFingerError as error:
            return JsonResponse(error.create_dict(), status=400)

    def post(self, request, *args, **kwargs):
        return self.on_request(request)