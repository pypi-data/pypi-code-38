from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import FormView

from saleboxdjango.lib.checkout import SaleboxCheckout


class SaleboxCheckoutBaseView(FormView):
    checkout_step = None

    def get_conf(self, name, default):
        return settings.SALEBOX['CHECKOUT'].get(name, default)

    def dispatch(self, request, *args, **kwargs):
        # friendlier error messages
        if self.checkout_step is None:
            raise Exception('You need to define a checkout_step')
        if self.form_class is None:
            raise Exception('You need to define a form_class')

        # get defaults
        user_must_be_authenticated = self.get_conf(
            'CHECKOUT_USER_MUST_BE_AUTHENTICATED',
            True
        )
        user_not_authenticated_redirect = self.get_conf(
            'CHECKOUT_USER_NOT_AUTHENTICATED_REDIRECT',
            '/'
        )

        # check logged in
        if user_must_be_authenticated and not request.user.is_authenticated:
            return redirect(user_not_authenticated_redirect)

        # get checkout object
        self.sc = SaleboxCheckout(request)
        r = self.sc.page_redirect(self.checkout_step)
        if r is not None:
            return redirect(r)

        # store the request in the object
        self.request = request

        # default dispatch action
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        valid = self.form_valid_pre_redirect(form)
        if not valid:
            return self.form_invalid(form)

        # set as complete and redirect to the next step
        r = self.sc.set_completed(self.checkout_step, self.request)
        if r is None:
            raise Exception('There is no next checkout step to redirect to...')
        else:
            return redirect(r)

    def form_valid_pre_redirect(self, form):
        # add you own code here
        # self.request is available
        # return True if form handled correctly
        # return False to re-show the page as form_invalid()
        #
        return True

    def get_additional_context_data(self, context):
        # add your custom code here, e.g...
        #     context['foo'] = 'bar'
        # ...then just return it
        # self.request is available
        #
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.sc.get_raw_data()

        total_price = data['basket']['sale_price']
        if data['shipping_method']['id'] is not None:
            total_price += data['shipping_method']['price']

        context['checkout'] = {
            'data': data,
            'nav': self.sc.get_checkout_nav(self.checkout_step),
            'step': self.checkout_step,
            'total_price': total_price
        }
        return self.get_additional_context_data(context)
