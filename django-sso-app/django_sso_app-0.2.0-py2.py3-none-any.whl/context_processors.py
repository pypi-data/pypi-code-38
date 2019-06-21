from . import settings


def sso_cookie_domain(request):
    return {
        "sso_cookie_domain": settings.DJANGO_SSO_COOKIE_DOMAIN
    }
