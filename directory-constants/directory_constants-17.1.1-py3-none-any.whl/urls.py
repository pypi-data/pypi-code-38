import functools
from urllib.parse import urljoin

from django.conf import settings


def get_url(url_name, default=None):
    return getattr(settings, url_name, None) or default


# SERVICES
SERVICES_GREAT_DOMESTIC = get_url(
    'DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC',
    'https://www.great.gov.uk'
)
build_great_url = functools.partial(urljoin, SERVICES_GREAT_DOMESTIC)
SERVICES_GREAT_INTERNATIONAL = get_url(
    'DIRECTORY_CONSTANTS_URL_GREAT_INTERNATIONAL',
    'https://www.great.gov.uk/international/'
)
build_great_international_url = functools.partial(
    urljoin, SERVICES_GREAT_INTERNATIONAL)
SERVICES_INVEST = get_url(
    'DIRECTORY_CONSTANTS_URL_INVEST',
    'https://invest.great.gov.uk'
)
SERVICES_EVENTS = get_url(
    'DIRECTORY_CONSTANTS_URL_EVENTS',
    'https://www.events.great.gov.uk'
)
SERVICES_SOO = get_url(
    'DIRECTORY_CONSTANTS_URL_SELLING_ONLINE_OVERSEAS',
    'https://selling-online-overseas.export.great.gov.uk'
)
SERVICES_FAS = get_url(
    'DIRECTORY_CONSTANTS_URL_FIND_A_SUPPLIER',
    'https://www.great.gov.uk/trade/'
)
SERVICES_ISD = get_url(
    'DIRECTORY_CONSTANTS_URL_INVESTMENT_SUPPORT_DIRECTORY',
    'https://www.great.gov.uk/investment-support-directory/'
)
build_fas_url = functools.partial(urljoin, SERVICES_FAS)
build_isd_url = functools.partial(urljoin, SERVICES_ISD)
FAS_SEARCH = build_fas_url('search/')
FAS_INVESTMENT_SUPPORT_DIRECTORY = \
    build_isd_url('')
FAS_INVESTMENT_SUPPORT_DIRECTORY_SEARCH = \
    build_isd_url('search/')
SERVICES_SSO = get_url(
    'DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON',
    build_great_url('sso/')
)
SERVICES_EXOPPS = get_url(
    'DIRECTORY_CONSTANTS_URL_EXPORT_OPPORTUNITIES',
    build_great_url('export-opportunities/')
)
SERVICES_FAB = get_url(
    'DIRECTORY_CONSTANTS_URL_FIND_A_BUYER',
    build_great_url('find-a-buyer/')
)
SERVICES_SSO_PROFILE = get_url(
    'DIRECTORY_CONSTANTS_URL_SSO_PROFILE',
    build_great_url('profile/')
)

# Export readiness/great domestic article sections
ADVICE = build_great_url('advice/')
ADVICE_CREATE_AN_EXPORT_PLAN = build_great_url('advice/create-an-export-plan/')
ADVICE_FIND_AN_EXPORT_MARKET = build_great_url('advice/find-an-export-market/')
ADVICE_DEFINE_ROUTE_TO_MARKET = build_great_url(
    'advice/define-route-to-market/'
)
ADVICE_GET_EXPORT_FINANCE_AND_FUNDING = build_great_url(
    'advice/get-export-finance-and-funding/'
)
ADVICE_MANAGE_PAYMENT_FOR_EXPORT_ORDERS = build_great_url(
    'advice/manage-payment-for-export-orders/'
)
ADVICE_PREPARE_TO_DO_BUSINESS_IN_A_FOREIGN_COUNTRY = build_great_url(
    'advice/prepare-to-do-business-in-a-foreign-country/'
)
ADVICE_MANAGE_LEGAL_AND_ETHICAL_COMPLIANCE = build_great_url(
    'advice/manage-legal-and-ethical-compliance/'
)
ADVICE_PREPARE_FOR_EXPORT_PROCEDURES_AND_LOGISTICS = build_great_url(
    'advice/prepare-for-export-procedures-and-logistics/'
)

SEARCH = build_great_url('search/')
MARKETS = build_great_url('markets/')
GET_FINANCE = build_great_url('get-finance/')
GREAT_DOMESTIC_NEWS = build_great_url('news/')
SERVICES = build_great_url('services/')
TERMS_AND_CONDITIONS = build_great_url('terms-and-conditions/')
ABOUT = build_great_url('about/')
PRIVACY_AND_COOKIES = build_great_url('privacy-and-cookies/')
PERFORMANCE_DASHBOARD = build_great_url('performance-dashboard/')
FEEDBACK = build_great_url('contact/feedback/')
CONTACT_US = build_great_url('contact/')
OFFICE_FINDER = build_great_url('contact/office-finder/')

DIT = (
    'https://www.gov.uk/government/organisations/'
    'department-for-international-trade'
)

# Great international
GREAT_INTERNATIONAL = SERVICES_GREAT_INTERNATIONAL
GREAT_INTERNATIONAL_NEWS = build_great_international_url('news/')
GREAT_INTERNATIONAL_HOW_TO_DO_BUSINESS_WITH_THE_UK = \
    build_great_international_url('how-to-do-business-with-the-uk/')
GREAT_INTERNATIONAL_INDUSTRIES = build_great_international_url('industries/')
GREAT_INTERNATIONAL_HOW_TO_SETUP_IN_THE_UK = \
    build_great_international_url('how-to-setup-in-the-uk/')
GREAT_INTERNATIONAL_CAPITAL_INVEST_LANDING_PAGE = \
    build_great_international_url('capital-invest')
GREAT_INTERNATIONAL_HOW_TO_SET_UP_VISAS_AND_MIGRATION = \
    build_great_international_url(
        'how-to-setup-in-the-uk/uk-visas-and-migration/'
    )
GREAT_INTERNATIONAL_HOW_TO_SET_UP_TAX_AND_INCENTIVES = \
    build_great_international_url(
        'how-to-setup-in-the-uk/uk-tax-and-incentives/'
    )

# Invest
build_invest_url = functools.partial(urljoin, SERVICES_INVEST)
INVEST_INDUSTRIES = build_invest_url('industries/')
INVEST_SETUP_GUIDE = build_invest_url('uk-setup-guide/')
INVEST_CONTACT_US = build_invest_url('contact/')

# Legacy great/export readiness article/persona/triage urls
CUSTOM_PAGE = build_great_url('custom/')
EXPORTING_NEW = build_great_url('new/')
EXPORTING_OCCASIONAL = build_great_url('occasional/')
EXPORTING_REGULAR = build_great_url('regular/')
GUIDANCE_MARKET_RESEARCH = build_great_url('market-research/')
GUIDANCE_CUSTOMER_INSIGHT = build_great_url('customer-insight/')
GUIDANCE_FINANCE = build_great_url('finance/')
GUIDANCE_BUSINESS_PLANNING = build_great_url('business-planning/')
GUIDANCE_GETTING_PAID = build_great_url('getting-paid/')
GUIDANCE_OPERATIONS_AND_COMPLIANCE = build_great_url(
    'operations-and-compliance/'
)
