from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import View

from saleboxdjango.lib.address import SaleboxAddress


class SaleboxBaseView(View):
    user_must_be_authenticated = True
    http_method_names = ['post']

    form = None  # django form
    action = None  # name of action performed
    status = None  # action outcome

    redirect = None  # url to redirect to (if applicable)
    state = None  # optional extra string data, passed thru
    results_csv = ''  # csv of requested results (if applicable)
    results = {}  # dict of results to return

    def add_json(self, key):
        if getattr(self, key, None):
            self.results[key] = getattr(self, key)

    def add_querystring(self, key, value):
        if value:
            self.redirect = '%s%s%s=%s' % (
                self.redirect,
                '&' if '?' in self.redirect else '?',
                key,
                value
            )

    def form_valid(self, request):
        self.status = 'success'

    def form_invalid(self, request):
        self.status = 'fail'

    def init_class(self, request):
        pass

    def post(self, request):
        if self.user_must_be_authenticated and not request.user.is_authenticated:
            return JsonResponse({'error': 'unauthenticated'})

        self.form = self.form(request.POST)
        if self.form.is_valid():
            # retrieve form values
            self.redirect = self.form.cleaned_data['redirect']
            self.state = self.form.cleaned_data['state']
            if self.form.cleaned_data['results']:
                self.results_csv = self.form.cleaned_data['results']

            # perform task
            self.init_class(request)
            self.form_valid(request)
        else:
            # handle error
            self.form_invalid(request)

        # redirect if applicable
        if self.redirect:
            self.add_querystring('state', self.state)
            self.add_querystring('action', self.action)
            self.add_querystring('status', self.status)
            return redirect(self.redirect)

        # return json
        self.add_json('state')
        self.add_json('action')
        self.add_json('status')
        return JsonResponse(self.results)
