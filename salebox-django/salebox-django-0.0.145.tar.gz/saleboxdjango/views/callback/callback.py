from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from saleboxdjango.models import CallbackStore, CheckoutStore, CheckoutStoreUpdate


@method_decorator(csrf_exempt, name='dispatch')
class SaleboxCallbackView(View):
    get_redirect = None
    post_redirect = None

    def dispatch(self, request, *args, **kwargs):
        CallbackStore(
            ip_address=request.META['REMOTE_ADDR'],
            method=request.method.lower(),
            post=request.POST
        ).save()

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        if self.get_redirect is not None:
            return HttpResponseRedirect(self.get_redirect)
        return HttpResponse('OK')

    def post(self, request):
        if self.post_redirect is not None:
            return HttpResponseRedirect(self.post_redirect)
        return HttpResponse('OK')

    def _get_store(self, uuid, visible_id):
        return CheckoutStore \
                .objects \
                .filter(uuid=uuid) \
                .filter(visible_id=visible_id) \
                .first()

    def _save_store_update(self, store, status, data):
        CheckoutStoreUpdate(
            store=store,
            status=status,
            data=data,
        ).save()
