import time

from django.conf import settings
from django.forms.models import model_to_dict
from django.utils.translation import get_language

from saleboxdjango.models import CheckoutStore, UserAddress


class SaleboxCheckout:
    def __init__(self, request):
        self._init_sequence()
        self._init_session(request)
        self._write_session(request)

    def get_checkout_nav(self, curr_page_name=None):
        nav = {
            'order': [],
            'lookup': {},
            'previous': None,
            'next': None
        }

        for pos, s in enumerate(self.sequence['order']):
            accessible = curr_page_name is not None and self.sequence['lookup'][s]['accessible']
            current = s == curr_page_name

            # set previous / next item helpers
            if current:
                if pos > 0:
                    tmp = self.sequence['order'][pos - 1]
                    nav['previous'] = {
                        'accessible': self.sequence['lookup'][tmp]['accessible'],
                        'label': self.sequence['lookup'][tmp]['label'],
                        'page_name': tmp,
                        'path': self.sequence['lookup'][tmp]['path'],
                    }
                if pos < len(self.sequence['order']) - 1:
                    tmp = self.sequence['order'][pos + 1]
                    nav['next'] = {
                        'accessible': self.sequence['lookup'][tmp]['accessible'],
                        'label': self.sequence['lookup'][tmp]['label'],
                        'page_name': tmp,
                        'path': self.sequence['lookup'][tmp]['path'],
                    }

            # set lookup
            nav['lookup'][s] = {
                'accessible': accessible,
                'current': current,
            }

            # set order
            nav['order'].append({
                'accessible': accessible,
                'current': current,
                'label': self.sequence['lookup'][s]['label'],
                'page_name': s,
                'path': self.sequence['lookup'][s]['path'],
            })

        for pos, n in enumerate(nav['order']):
            try:
                nav['order'][pos]['previous_accessible'] = nav['order'][pos - 1]['accessible']
            except:
                nav['order'][pos]['previous_accessible'] = False
            try:
                nav['order'][pos]['next_accessible'] = nav['order'][pos + 1]['accessible']
            except:
                nav['order'][pos]['next_accessible'] = False

        return nav

    def get_raw_data(self):
        return self.data

    def get_last_accessible_page(self):
        for o in reversed(self.sequence['order']):
            if self.sequence['lookup'][o]['accessible']:
                return self.sequence['lookup'][o]['path']

        return None

    def get_current_page_path(self, path_name):
        return self.sequence['lookup'][path_name]['path']

    def get_next_page(self, page_name):
        next = self.sequence['order'].index(page_name) + 1
        if next < len(self.sequence['order']):
            return self.sequence['lookup'][
                self.sequence['order'][next]
            ]['path']
        else:
            return None

    def page_redirect(self, page_name):
        if page_name not in self.sequence['order']:
            raise Exception('Unrecognised SaleboxCheckout page_name: %s' % page_name)

        # if basket empty, redirect to the pre-checkout page, e.g.
        # typically the shopping basket
        if len(self.data['basket']) == 0:
            return settings.SALEBOX['CHECKOUT']['PRE_URL']

        # if this page is not marked accessible, i.e. the user is
        # trying to jump steps in the process, redirect them to
        # the 'last known good' page
        if not self.is_page_accessible(page_name):
            return self.get_last_accessible_page()

        return None

    def is_page_accessible(self, page_name):
        try:
            return self.sequence['lookup'][page_name]['accessible']
        except:
            return False

    def save_to_store(self, user, gateway_code='default', sent_to_gateway=True, visible_id=None):
        data = self.get_raw_data()
        cs = CheckoutStore(
            visible_id=visible_id,
            user=user.id if user else None,
            gateway_code=gateway_code,
            status=20 if sent_to_gateway else 10,
            data=self.get_raw_data()
        )
        cs.save()
        return cs

    def set_basket(self, basket, request, reset_completed=True, reset_checkout=True):
        if reset_checkout:
            self._init_data()
        if reset_completed:
            self.data['completed'] = []

        # populate data object
        self.data['basket'] = basket.get_raw_data()['basket']
        self._write_session(request)

        # return url to redirect to
        return self.sequence['lookup'][self.sequence['order'][0]]['path']

    def set_completed(self, page_name, request):
        self.data['completed'].append(page_name)
        self._update_sequence()
        self._write_session(request)
        return self.get_next_page(page_name)

    def set_invoice_address(self, required, id, meta, request):
        if id is None:
            self.data['invoice_address']['address'] = None
        else:
            self.data['invoice_address']['address'] = model_to_dict(UserAddress.objects.get(id=id))
        self.data['invoice_address']['id'] = id
        self.data['invoice_address']['meta'] = meta
        self.data['invoice_address']['required'] = required
        self._write_session(request)

    def set_payment_method(self, id, meta, request):
        self.data['payment_method'] = {
            'id': int(id),
            'meta': meta
        }
        self._write_session(request)

    def set_shipping_address(self, required, id, meta, request):
        self.data['shipping_address']['address'] = model_to_dict(UserAddress.objects.get(id=id))
        self.data['shipping_address']['id'] = id
        self.data['shipping_address']['meta'] = meta
        self.data['shipping_address']['required'] = required
        self._write_session(request)

    def set_shipping_method(self, id, label, price, meta, request):
        self.data['shipping_method'] = {
            'id': id,
            'label': label,
            'price': price,
            'meta': meta
        }
        self._write_session(request)

    def _init_data(self):
        self.data = {
            'basket': {},
            'completed': [],
            'data': {},
            'invoice_address': {
                'address': None,
                'id': None,
                'meta': None,
                'required': None,
            },
            'last_seen': int(time.time()),
            'payment_method': {
                'id': None,
                'meta': None,
            },
            'shipping_address': {
                'address': None,
                'id': None,
                'meta': None,
                'required': None,
            },
            'shipping_method': {
                'id': None,
                'label': None,
                'meta': None,
                'price': None,
            }
        }

    def _init_sequence(self):
        self.sequence = {
            'order': [],
            'lookup': {}
        }

        # use language url prefix? e.g. /en/checkout/address
        url_prefix = ''
        if settings.SALEBOX['CHECKOUT'].get('URL_LANGUAGE_PREFIX', False):
            url_prefix = '/%s' % get_language()

        for i, s in enumerate(settings.SALEBOX['CHECKOUT']['SEQUENCE']):
            self.sequence['order'].append(s[0])
            self.sequence['lookup'][s[0]] = {
                'label': s[2] if len(s) == 3 else s[0],
                'path': '%s%s' % (url_prefix, s[1]),
                'position': i,
                'complete': False,
                'accessible': i == 0
            }

    def _init_session(self, request):
        self._init_data()

        # attempt to import data from the session
        request.session.setdefault('saleboxcheckout', None)
        if request.session['saleboxcheckout'] is not None:
            tmp = request.session['saleboxcheckout']
            if int(time.time()) - tmp['last_seen'] < 60 * 60:  # 1 hr
                self.data = request.session['saleboxcheckout']

        # update data
        self._update_sequence()
        self.data['last_seen'] = int(time.time())

    def _update_sequence(self):
        for i, o in enumerate(self.sequence['order']):
            if o in self.data['completed']:
                self.sequence['lookup'][o]['complete'] = True
                self.sequence['lookup'][o]['accessible'] = True
                try:
                    self.sequence['lookup'][
                        self.sequence['order'][i + 1]
                    ]['accessible'] = True
                except:
                    pass

    def _write_session(self, request):
        if len(self.data['basket']) == 0:
            request.session['saleboxcheckout'] = None
        else:
            request.session['saleboxcheckout'] = self.data
