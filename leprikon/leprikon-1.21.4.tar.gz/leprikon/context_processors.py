from django.utils.functional import SimpleLazyObject

from .models.leprikonsite import LeprikonSite


def leprikonsite(request):
    return {'leprikonsite': SimpleLazyObject(LeprikonSite.objects.get_current)}
