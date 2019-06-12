class Sender(dict):
    def __init__(self, email_address, country_code=None):
        super().__init__(
            email_address=email_address, country_code=country_code
        )


class SpamControl(dict):
    def __init__(self, contents):
        super().__init__(contents=contents)


class FormSession:

    KEY_INGRESS_URL = 'DIRECTORY_API_FORMS_INGRESS_URL'
    KEY_FUNNEL_STEPS = 'DIRECTORY_API_FORMS_FUNNEL_STEPS'

    def __init__(self, request):
        self.session = request.session

    @property
    def ingress_url(self):
        return self.session.get(self.KEY_INGRESS_URL, '')

    @ingress_url.setter
    def ingress_url(self, ingress_url):
        self.session[self.KEY_INGRESS_URL] = ingress_url

    @ingress_url.deleter
    def ingress_url(self):
        self.session.pop(self.KEY_INGRESS_URL, None)

    @property
    def funnel_steps(self):
        self.funnel_steps = self.session.get(self.KEY_FUNNEL_STEPS, [])
        return self.session[self.KEY_FUNNEL_STEPS]

    @funnel_steps.setter
    def funnel_steps(self, steps):
        self.session[self.KEY_FUNNEL_STEPS] = steps

    @funnel_steps.deleter
    def funnel_steps(self):
        self.session.pop(self.KEY_FUNNEL_STEPS, None)

    def clear(self):
        del self.funnel_steps
        del self.ingress_url


class FormSessionMixin:
    form_session_class = FormSession

    def dispatch(self, request, *args, **kwargs):
        self.form_session = self.form_session_class(request=request)
        return super().dispatch(request=request, *args, **kwargs)

    def get(self, *args, **kwargs):
        if not self.form_session.ingress_url:
            ingress_url = self.request.META.get('HTTP_REFERER')
            self.form_session.ingress_url = ingress_url
        return super().get(*args, **kwargs)
