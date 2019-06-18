from django.conf import settings
from .models import SiteProperty, Links, Menu
from autopost.models import Category
import random


def site_info(request):
    site_property = SiteProperty.objects.filter(site__domain=request.site.domain).first()
    links = Links.objects.filter(status=1).filter(site=request.site).all()
    categories = Category.objects.filter(status=2).filter(site=request.site).all()
    menu = Menu.objects.filter(status=1).filter(site=request.site).all()[:7]
    return {
        'site': site_property,
        'links': links,
        'menu': menu,
        'global_category': categories,
        'settings': settings,
        'version': settings.STATIC_VERSION if not settings.DEBUG else random.randint(10000, 999999),
    }
