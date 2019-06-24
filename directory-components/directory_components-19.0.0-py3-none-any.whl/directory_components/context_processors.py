from directory_constants import urls

from django.conf import settings

from directory_components.helpers import add_next


def sso_processor(request):
    url = request.build_absolute_uri()
    return {
        'sso_user': request.sso_user,
        'sso_is_logged_in': request.sso_user is not None,
        'sso_login_url': add_next(settings.SSO_PROXY_LOGIN_URL, url),
        'sso_register_url': add_next(settings.SSO_PROXY_SIGNUP_URL, url),
        'sso_logout_url': add_next(settings.SSO_PROXY_LOGOUT_URL, url),
        'sso_profile_url': settings.SSO_PROFILE_URL,
    }


def analytics(request):
    return {
        'directory_components_analytics': {
            'GOOGLE_TAG_MANAGER_ID': settings.GOOGLE_TAG_MANAGER_ID,
            'GOOGLE_TAG_MANAGER_ENV': settings.GOOGLE_TAG_MANAGER_ENV,
            'UTM_COOKIE_DOMAIN': settings.UTM_COOKIE_DOMAIN,
        }
    }


def cookie_notice(request):
    return {
        'directory_components_cookie_notice': {
            'PRIVACY_COOKIE_DOMAIN': settings.PRIVACY_COOKIE_DOMAIN
        }
    }


def header_footer_processor(request):
    advice_urls = {
        'create_an_export_plan': urls.ADVICE_CREATE_AN_EXPORT_PLAN,
        'find_an_export_market': urls.ADVICE_FIND_AN_EXPORT_MARKET,
        'define_route_to_market': urls.ADVICE_DEFINE_ROUTE_TO_MARKET,
        'get_export_finance_and_funding':
            urls.ADVICE_GET_EXPORT_FINANCE_AND_FUNDING,
        'manage_payment_for_export_orders':
            urls.ADVICE_MANAGE_PAYMENT_FOR_EXPORT_ORDERS,
        'prepare_to_do_business_in_a_foreign_country':
            urls.ADVICE_PREPARE_TO_DO_BUSINESS_IN_A_FOREIGN_COUNTRY,
        'manage_legal_and_ethical_compliance':
            urls.ADVICE_MANAGE_LEGAL_AND_ETHICAL_COMPLIANCE,
        'prepare_for_export_procedures_and_logistics':
            urls.ADVICE_PREPARE_FOR_EXPORT_PROCEDURES_AND_LOGISTICS,
    }
    header_footer_urls = {
        'about': urls.ABOUT,
        'dit': urls.DIT,
        'get_finance': urls.GET_FINANCE,
        'ukef': urls.GET_FINANCE,
        'performance': urls.PERFORMANCE_DASHBOARD,
        'privacy_and_cookies': urls.PRIVACY_AND_COOKIES,
        'terms_and_conditions': urls.TERMS_AND_CONDITIONS,
        'fas': urls.SERVICES_FAS,
        'advice': urls.ADVICE,
        'markets': urls.MARKETS,
        'search': urls.SEARCH,
        'services': urls.SERVICES,
        'domestic_news': urls.GREAT_DOMESTIC_NEWS,
        'international_news': urls.GREAT_INTERNATIONAL_NEWS,
        'how_to_do_business_with_the_uk':
            urls.GREAT_INTERNATIONAL_HOW_TO_DO_BUSINESS_WITH_THE_UK,
        'industries':
            urls.GREAT_INTERNATIONAL_INDUSTRIES,
        'market_access': urls.build_great_url('report-trade-barrier/')
    }
    header_footer_urls = {**header_footer_urls, **advice_urls}
    return {'header_footer_urls': header_footer_urls}


def invest_header_footer_processor(request):
    invest_header_footer_urls = {
        'industries': urls.INVEST_INDUSTRIES,
        'uk_setup_guide': urls.INVEST_SETUP_GUIDE,
    }
    return {'invest_header_footer_urls': invest_header_footer_urls}


def urls_processor(request):
    services_urls = {
        'contact_us': urls.CONTACT_US,
        'events': urls.SERVICES_EVENTS,
        'exopps': urls.SERVICES_EXOPPS,
        'exred': urls.SERVICES_GREAT_DOMESTIC,
        'great_domestic': urls.SERVICES_GREAT_DOMESTIC,
        'great_international': urls.GREAT_INTERNATIONAL,
        'fab': urls.SERVICES_FAB,
        'fas': urls.SERVICES_FAS,
        'feedback': urls.FEEDBACK,
        'office_finder': urls.OFFICE_FINDER,
        'invest': urls.SERVICES_INVEST,
        'soo': urls.SERVICES_SOO,
        'sso': urls.SERVICES_SSO,
        'uk_setup_guide': urls.GREAT_INTERNATIONAL_HOW_TO_SETUP_IN_THE_UK,
        'isd': urls.FAS_INVESTMENT_SUPPORT_DIRECTORY,
    }
    return {'services_urls': services_urls}


def feature_flags(request):
    return {'features': settings.FEATURE_FLAGS}
