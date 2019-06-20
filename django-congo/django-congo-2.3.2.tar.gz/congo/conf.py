# -*- coding: utf-8 -*-
import os
import re

from appconf import AppConf
from django.conf import settings as django_settings
from django.core.cache import DEFAULT_CACHE_ALIAS
from django.utils.translation import ugettext_lazy as _

settings = django_settings


class CongoAppConf(AppConf):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # sites

    SITE_MODEL = '' # eg 'maintenance.Site'

    # logs

    LOG_MODEL = '' # eg 'maintenance.Log'
    LOG_ROOT = os.path.join(settings.BASE_DIR, 'logs')
    COMMON_ERRORS_IGNORE_LIST = []
    COMMON_WARNINGS_IGNORE_LIST = []

    # audit

    AUDIT_MODEL = '' # eg 'maintenance.Audit'
    TEST_MODULE = '' # eg 'maintenance.tests'
    TEST_CHOICE_PATH = '' # eg os.path.join(BASE_DIR, *JOBS_MODULE.split('.'))

    # cron

    CRON_MODEL = '' # eg 'maintenance.Cron'
    JOBS_MODULE = '' # eg 'maintenance.jobs'
    JOB_CHOICE_PATH = '' # eg os.path.join(BASE_DIR, *JOBS_MODULE.split('.'))

    # url redirects

    URL_REDIRECT_MODEL = '' # eg 'maintenance.UrlRedirect'

    # cache

    CACHE_KEY_APPEND_SITE_ID = True
    CACHE_KEY_APPEND_LANGUAGE = True
    TEMPLATE_CACHE_BACKEND = DEFAULT_CACHE_ALIAS # eg 'template_cache'
    TEMPLATE_CACHE_KEY_APPEND_LANGUAGE = not CACHE_KEY_APPEND_LANGUAGE

    # admin

    ADMIN_MODEL = 'congo.admin.admin.BaseModelAdmin'
    ADMIN_PATH = '/admin/'
    ADMIN_LANGUAGE_CODE = settings.LANGUAGE_CODE

    # accounts

    AUTHENTICATION_DOMAIN = (lambda: settings.ALLOWED_HOSTS[0] if len(settings.ALLOWED_HOSTS) else 'example.com')()

    # external

    GOOGLE_BROWSER_API_KEY = None
    GOOGLE_SERVER_API_KEY = None

    # secure

    SSL_FORCED = False
    SSL_ENABLED = False
    IGNORABLE_SSL_URLS = ()

    # middleware

    SPACELESS_ENABLED = True

    TEXT_IMAGE_PATH = os.path.join(settings.STATIC_ROOT, 'logo.txt')

    STATICFILES_URLS = (
        '/__debug__/',
        '/media/',
        '/static/',
    )

    IGNORABLE_SPACELESS_URLS = (
        re.compile(r'/admin/'),
        re.compile(r'/admin_tools/'),
        re.compile(r'/autocomplete/'),
        re.compile(r'/cron/'),
        re.compile(r'/api/'),
        re.compile(r'/rss/'),
        re.compile(r'/newsletter/'),
        re.compile(r'/sitemap.xml'),
    )

    # communication

    DEFAULT_FROM_EMAIL_NAME = None

    EMAIL_PREMAILER_BASE_PATH = settings.BASE_DIR
    EMAIL_PROTOCOL = 'http' # protocol used in e-mail templates
    EMAIL_TEMPLATE_DOMAIN = (lambda: settings.ALLOWED_HOSTS[0] if len(settings.ALLOWED_HOSTS) else 'www.example.com')() # domain used as placeholder in e-mail templates

    EMAIL_SENDER_MODEL = '' # eg 'communication.EmailSender'
    EMAIL_RECIPIENT_GROUP_MODEL = '' # eg 'communication.EmailRecipientGroup'
    EMAIL_RECIPIENT_MODEL = '' # eg 'communication.EmailRecipient'
    EMAIL_MESSAGE_MODEL = '' # eg 'communication.EmailMessage'
    EMAIL_MESSAGE_QUEUE_MODEL = '' # eg 'communication.EmailMessageQueue'

    SMS_RECIPIENT_GROUP_MODEL = '' # eg 'communication.SMSRecipientGroup'
    SMS_RECIPIENT_MODEL = '' # eg 'communication.SMSRecipient'
    SMS_MESSAGE_MODEL = '' # eg 'communication.SMSMessage'
    SMS_MESSAGE_QUEUE_MODEL = '' # eg 'communication.SMSMessageQueue'

    SMS_SENDER_LIST = (
        ('ECO', _(u"Losowy numer")),
    )
    SMS_BACKEND = 'congo.communication.backends.console.SMSBackend' # eg 'congo.communication.backends.smsapi.SMSBackend'
    SMSAPI_USER = '' # eg 'user'
    SMSAPI_PASSWORD = '' # eg 'abc123'

    # gallery

    BLANK_IMAGE_FILENAME = 'blank_image.jpg'
    BLANK_IMAGE_PATH = os.path.join(settings.STATIC_ROOT, 'img', 'blank_image')
    BLANK_IMAGE_URL = '/static/img/blank_image/'

    WATERMARK_PATH = os.path.join(settings.STATIC_ROOT, 'img', 'watermarks')

    DEFAULT_IMAGE_WIDTH = 800
    DEFAULT_IMAGE_HEIGHT = 800

    WATERMARK_MIN_WIDTH = 500
    WATERMARK_MIN_HEIGHT = 500

    WATERMARK_HORIZONTAL_POSITION = 'R' # Left, Center, Right
    WATERMARK_VERTICAL_POSITION = 'B' # Top, Center, Bottom

    # meta class

    DEFAULT_META_TITLE = "Congo Project"
    DEFAULT_META_TITLE_DIVIDER = "-"
    APPEND_DEFAULT_TITLE = True
    DEFAULT_META_DESCRIPTION = "Tools for faster and more efficient Django application developing"
    DEFAULT_META_IMAGE = ""

    # regex

    PHONE_REGEX = r'^(\+|00)?\d{9,15}$'
    PHONE_WITHOUT_AREA_CODE_REGEX = r'^\d{9,15}$'
    PRECISE_PHONE_REGEX = r'^(\+|00)(9[976]\d|8[987530]\d|6[987]\d|5[90]\d|42\d|3[875]\d|2[98654321]\d|9[8543210]|8[6421]|6[6543210]|5[87654321]|4[987654310]|3[9643210]|2[70]|7|1)( )?\d{1,14}$'
    URL_REGEX = r'^(http|https)://[\w-]+(\.[\w-]+)+([\w.,@?^=%&amp;:/~+#-]*[\w@?^=%&amp;/~+#-])?'
    POLISH_ZIP_CODE_REGEX = r'[0-9]{2}-[0-9]{3}$'

    REGEX = {
        'phone' : PHONE_REGEX,
        'phone_without_area_code' : PHONE_WITHOUT_AREA_CODE_REGEX,
        'precise_phone' : PRECISE_PHONE_REGEX,
        'url' : URL_REGEX,
        'polish_zip_code': POLISH_ZIP_CODE_REGEX
    }

    # po2parler & parler2po
    PARLER_2_PO_DEFAULT_LANG_FROM = None
    PARLER_2_PO_DEFAULT_LANG_TO = None
    PARLER_2_PO_CONFIG = {}
    PARLER_2_PO_MODELS = []

    # countries

    # https://github.com/SmileyChris/django-countries/blob/master/django_countries/data.py#L46
    COUNTRIES = (
        ('AF', _(u"Afganistan")),
        ('AX', _(u"Wyspy Alandzkie")),
        ('AL', _(u"Albania")),
        ('DZ', _(u"Algeria")),
        ('AS', _(u"Samoa Amerykańskie")),
        ('AD', _(u"Andora")),
        ('AO', _(u"Angola")),
        ('AI', _(u"Anguilla")),
        ('AQ', _(u"Antarktyda")),
        ('AG', _(u"Antigua i Barbuda")),
        ('AR', _(u"Argentyna")),
        ('AM', _(u"Armenia")),
        ('AW', _(u"Aruba")),
        ('AU', _(u"Australia")),
        ('AT', _(u"Austria")),
        ('AZ', _(u"Azerbejdżan")),
        ('BS', _(u"Bahamy")),
        ('BH', _(u"Bahrajn")),
        ('BD', _(u"Bangladesz")),
        ('BB', _(u"Barbados")),
        ('BY', _(u"Białoruś")),
        ('BE', _(u"Belgia")),
        ('BZ', _(u"Belize")),
        ('BJ', _(u"Benin")),
        ('BM', _(u"Bermudy")),
        ('BT', _(u"Bhutan")),
        ('BO', _(u"Boliwia")),
        ('BQ', _(u"Bonaire, Sint Eustatius i Saba")),
        ('BA', _(u"Bośnia i Hercegowina")),
        ('BW', _(u"Botswana")),
        ('BV', _(u"Wyspa Bouveta")),
        ('BR', _(u"Brazylia")),
        ('IO', _(u"Brytyjskie Terytorium Oceanu Indyjskiego")),
        ('BN', _(u"Brunei")),
        ('BG', _(u"Bułgaria")),
        ('BF', _(u"Burkina Faso")),
        ('BI', _(u"Burundi")),
        ('CV', _(u"Republika Zielonego Przylądka")),
        ('KH', _(u"Kambodża")),
        ('CM', _(u"Kamerun")),
        ('CA', _(u"Kanada")),
        ('KY', _(u"Kajmany")),
        ('CF', _(u"Republika Środkowoafrykańska")),
        ('TD', _(u"Czad")),
        ('CL', _(u"Chile")),
        ('CN', _(u"Chiny")),
        ('CX', _(u"Wyspa Bożego Narodzenia")),
        ('CC', _(u"Wyspy Kokosowe")),
        ('CO', _(u"Kolumbia")),
        ('KM', _(u"Komory")),
        ('CD', _(u"Kongo")),
        ('CG', _(u"Kongo")),
        ('CK', _(u"Wyspy Cooka")),
        ('CR', _(u"Kostaryka")),
        ('CI', _(u"Wybrzeże Kości Słoniowej")),
        ('HR', _(u"Chorwacja")),
        ('CU', _(u"Kuba")),
        ('CW', _(u"Curaçao")),
        ('CY', _(u"Cypr")),
        ('CZ', _(u"Czechy")),
        ('DK', _(u"Dania")),
        ('DJ', _(u"Dżibuti")),
        ('DM', _(u"Dominika")),
        ('DO', _(u"Dominikana")),
        ('EC', _(u"Ekwador")),
        ('EG', _(u"Egipt")),
        ('SV', _(u"Salwador")),
        ('GQ', _(u"Gwinea Równikowa")),
        ('ER', _(u"Erytrea")),
        ('EE', _(u"Estonia")),
        ('ET', _(u"Etiopia")),
        ('FK', _(u"Falklandy")),
        ('FO', _(u"Wyspy Owcze")),
        ('FJ', _(u"Fidżi")),
        ('FI', _(u"Finlandia")),
        ('FR', _(u"Francja")),
        ('GF', _(u"Gujana Francuska")),
        ('PF', _(u"Polinezja Francuska")),
        ('TF', _(u"Francuskie Terytoria Południowe i Antarktyczne")),
        ('GA', _(u"Gabon")),
        ('GM', _(u"Gambia")),
        ('GE', _(u"Gruzja")),
        ('DE', _(u"Niemcy")),
        ('GH', _(u"Ghana")),
        ('GI', _(u"Gibraltar")),
        ('GR', _(u"Grecja")),
        ('GL', _(u"Grenlandia")),
        ('GD', _(u"Grenada")),
        ('GP', _(u"Gwadelupa")),
        ('GU', _(u"Guam")),
        ('GT', _(u"Gwatemala")),
        ('GG', _(u"Guernsey")),
        ('GN', _(u"Gwinea")),
        ('GW', _(u"Gwinea Bissau")),
        ('GY', _(u"Gujana")),
        ('HT', _(u"Haiti")),
        ('HM', _(u"Wyspy Heard i McDonalda")),
        ('VA', _(u"Watykan")),
        ('HN', _(u"Honduras")),
        ('HK', _(u"Hongkong")),
        ('HU', _(u"Węgry")),
        ('IS', _(u"Islandia")),
        ('IN', _(u"Indie")),
        ('ID', _(u"Indonezja")),
        ('IR', _(u"Iran")),
        ('IQ', _(u"Irak")),
        ('IE', _(u"Irlandia")),
        ('IM', _(u"Wyspa Man")),
        ('IL', _(u"Izrael")),
        ('IT', _(u"Włochy")),
        ('JM', _(u"Jamajka")),
        ('JP', _(u"Japonia")),
        ('JE', _(u"Jersey")),
        ('JO', _(u"Jordania")),
        ('KZ', _(u"Kazachstan")),
        ('KE', _(u"Kenia")),
        ('KI', _(u"Kiribati")),
        ('KP', _(u"Korea Północna")),
        ('KR', _(u"Korea Południowa")),
        ('KW', _(u"Kuwejt")),
        ('KG', _(u"Kirgistan")),
        ('LA', _(u"Laos")),
        ('LV', _(u"Łotwa")),
        ('LB', _(u"Liban")),
        ('LS', _(u"Lesotho")),
        ('LR', _(u"Liberia")),
        ('LY', _(u"Libia")),
        ('LI', _(u"Liechtenstein")),
        ('LT', _(u"Litwa")),
        ('LU', _(u"Luksemburg")),
        ('MO', _(u"Makau")),
        ('MK', _(u"Macedonia")),
        ('MG', _(u"Madagaskar")),
        ('MW', _(u"Malawi")),
        ('MY', _(u"Malezja")),
        ('MV', _(u"Malediwy")),
        ('ML', _(u"Mali")),
        ('MT', _(u"Malta")),
        ('MH', _(u"Wyspy Marshalla")),
        ('MQ', _(u"Martynika")),
        ('MR', _(u"Mauretania")),
        ('MU', _(u"Mauritius")),
        ('YT', _(u"Majotta")),
        ('MX', _(u"Meksyk")),
        ('FM', _(u"Mikronezja")),
        ('MD', _(u"Mołdawia")),
        ('MC', _(u"Monako")),
        ('MN', _(u"Mongolia")),
        ('ME', _(u"Czarnogóra")),
        ('MS', _(u"Montserrat")),
        ('MA', _(u"Maroko")),
        ('MZ', _(u"Mozambik")),
        ('MM', _(u"Mjanma")),
        ('NA', _(u"Namibia")),
        ('NR', _(u"Nauru")),
        ('NP', _(u"Nepal")),
        ('NL', _(u"Holandia")),
        ('NC', _(u"Nowa Kaledonia")),
        ('NZ', _(u"Nowa Zelandia")),
        ('NI', _(u"Nikaragua")),
        ('NE', _(u"Niger")),
        ('NG', _(u"Nigeria")),
        ('NU', _(u"Niue")),
        ('NF', _(u"Norfolk")),
        ('MP', _(u"Mariany Północne")),
        ('NO', _(u"Norwegia")),
        ('OM', _(u"Oman")),
        ('PK', _(u"Pakistan")),
        ('PW', _(u"Palau")),
        ('PS', _(u"Palestyna")),
        ('PA', _(u"Panama")),
        ('PG', _(u"Papua-Nowa Gwinea")),
        ('PY', _(u"Paragwaj")),
        ('PE', _(u"Peru")),
        ('PH', _(u"Filipiny")),
        ('PN', _(u"Pitcairn")),
        ('PL', _(u"Polska")),
        ('PT', _(u"Portugalia")),
        ('PR', _(u"Portoryko")),
        ('QA', _(u"Katar")),
        ('RE', _(u"Reunion")),
        ('RO', _(u"Rumunia")),
        ('RU', _(u"Rosja")),
        ('RW', _(u"Rwanda")),
        ('BL', _(u"Saint-Barthélemy")),
        ('SH', _(u"Wyspa Świętej Heleny, Wyspa Wniebowstąpienia i Tristan da Cunha")),
        ('KN', _(u"Saint Kitts i Nevis")),
        ('LC', _(u"Saint Lucia")),
        ('MF', _(u"Saint-Martin")),
        ('PM', _(u"Saint-Pierre i Miquelon")),
        ('VC', _(u"Saint Vincent i Grenadyny")),
        ('WS', _(u"Samoa")),
        ('SM', _(u"San Marino")),
        ('ST', _(u"Wyspy Świętego Tomasza i Książęca")),
        ('SA', _(u"Arabia Saudyjska")),
        ('SN', _(u"Senegal")),
        ('RS', _(u"Serbia")),
        ('SC', _(u"Seszele")),
        ('SL', _(u"Sierra Leone")),
        ('SG', _(u"Singapur")),
        ('SX', _(u"Sint Maarten")),
        ('SK', _(u"Słowacja")),
        ('SI', _(u"Słowenia")),
        ('SB', _(u"Wyspy Salomona")),
        ('SO', _(u"Somalia")),
        ('ZA', _(u"Republika Południowej Afryki")),
        ('GS', _(u"Georgia Południowa i Sandwich Południowy")),
        ('SS', _(u"Sudan Południowy")),
        ('ES', _(u"Hiszpania")),
        ('LK', _(u"Sri Lanka")),
        ('SD', _(u"Sudan")),
        ('SR', _(u"Surinam")),
        ('SJ', _(u"Svalbard i Jan Mayen")),
        ('SZ', _(u"Suazi")),
        ('SE', _(u"Szwecja")),
        ('CH', _(u"Szwajcaria")),
        ('SY', _(u"Syria")),
        ('TW', _(u"Tajwan")),
        ('TJ', _(u"Tadżykistan")),
        ('TZ', _(u"Tanzania")),
        ('TH', _(u"Tajlandia")),
        ('TL', _(u"Timor Wschodni")),
        ('TG', _(u"Togo")),
        ('TK', _(u"Tokelau")),
        ('TO', _(u"Tonga")),
        ('TT', _(u"Trynidad i Tobago")),
        ('TN', _(u"Tunezja")),
        ('TR', _(u"Turcja")),
        ('TM', _(u"Turkmenistan")),
        ('TC', _(u"Turks i Caicos")),
        ('TV', _(u"Tuvalu")),
        ('UG', _(u"Uganda")),
        ('UA', _(u"Ukraina")),
        ('AE', _(u"Zjednoczone Emiraty Arabskie")),
        ('GB', _(u"Wielka Brytania")),
        ('UM', _(u"Dalekie Wyspy Mniejsze Stanów Zjednoczonych")),
        ('US', _(u"Stany Zjednoczone Ameryki")),
        ('UY', _(u"Urugwaj")),
        ('UZ', _(u"Uzbekistan")),
        ('VU', _(u"Vanuatu")),
        ('VE', _(u"Wenezuela")),
        ('VN', _(u"Wietnam")),
        ('VG', _(u"Brytyjskie Wyspy Dziewicze")),
        ('VI', _(u"Wyspy Dziewicze Stanów Zjednoczonych")),
        ('WF', _(u"Wallis i Futuna")),
        ('EH', _(u"Sahara Zachodnia")),
        ('YE', _(u"Jemen")),
        ('ZM', _(u"Zambia")),
        ('ZW', _(u"Zimbabwe")),
    )

    # python manage.py get_country_languages
    COUNTRY_LANGUAGES = {
        'AD': 'ca',
        'AE': 'ar',
        'AF': 'fa',
        'AG': 'en',
        'AI': 'en',
        'AL': 'sq',
        'AM': 'hy',
        'AO': 'pt',
        'AR': 'es',
        'AS': 'sm',
        'AT': 'de',
        'AU': 'en',
        'AW': 'nl',
        'AX': 'sv',
        'AZ': 'az',
        'BA': 'bs_Cyrl',
        'BB': 'en',
        'BD': 'bn',
        'BE': 'nl',
        'BF': 'fr',
        'BG': 'bg',
        'BH': 'ar',
        'BI': 'rn',
        'BJ': 'fr',
        'BL': 'fr',
        'BM': 'en',
        'BN': 'ms',
        'BO': 'es',
        'BQ': 'nl',
        'BR': 'pt',
        'BS': 'en',
        'BT': 'dz',
        'BW': 'en',
        'BY': 'be',
        'BZ': 'en',
        'CA': 'en',
        'CC': 'en',
        'CD': 'sw',
        'CF': 'fr',
        'CG': 'fr',
        'CH': 'de',
        'CI': 'fr',
        'CK': 'en',
        'CL': 'es',
        'CM': 'fr',
        'CN': 'zh',
        'CO': 'es',
        'CR': 'es',
        'CU': 'es',
        'CV': 'pt',
        'CW': 'pap',
        'CX': 'en',
        'CY': 'el',
        'CZ': 'cs',
        'DE': 'de',
        'DJ': 'ar',
        'DK': 'da',
        'DM': 'en',
        'DO': 'es',
        'DZ': 'ar',
        'EC': 'es',
        'EE': 'et',
        'EG': 'ar',
        'EH': 'ar',
        'ER': 'ti',
        'ES': 'es',
        'ET': 'am',
        'FI': 'fi',
        'FJ': 'en',
        'FK': 'en',
        'FM': 'en',
        'FO': 'fo',
        'FR': 'fr',
        'GA': 'fr',
        'GB': 'en',
        'GD': 'en',
        'GE': 'ka',
        'GF': 'fr',
        'GG': 'en',
        'GH': 'ak',
        'GI': 'en',
        'GL': 'kl',
        'GM': 'en',
        'GN': 'fr',
        'GP': 'fr',
        'GQ': 'es',
        'GR': 'el',
        'GT': 'es',
        'GU': 'en',
        'GW': 'pt',
        'GY': 'en',
        'HK': 'zh_Hant',
        'HN': 'es',
        'HR': 'hr',
        'HT': 'ht',
        'HU': 'hu',
        'ID': 'id',
        'IE': 'en',
        'IL': 'he',
        'IM': 'en',
        'IN': 'hi',
        'IO': 'en',
        'IQ': 'ar',
        'IR': 'fa',
        'IS': 'is',
        'IT': 'it',
        'JE': 'en',
        'JM': 'en',
        'JO': 'ar',
        'JP': 'ja',
        'KE': 'sw',
        'KG': 'ky',
        'KH': 'km',
        'KI': 'en',
        'KM': 'ar',
        'KN': 'en',
        'KP': 'ko',
        'KR': 'ko',
        'KW': 'ar',
        'KY': 'en',
        'KZ': 'ru',
        'LA': 'lo',
        'LB': 'ar',
        'LC': 'en',
        'LI': 'de',
        'LK': 'si',
        'LR': 'en',
        'LS': 'st',
        'LT': 'lt',
        'LU': 'fr',
        'LV': 'lv',
        'LY': 'ar',
        'MA': 'ar',
        'MC': 'fr',
        'MD': 'ro',
        'ME': 'sr_Latn',
        'MF': 'fr',
        'MG': 'mg',
        'MH': 'en',
        'MK': 'mk',
        'ML': 'fr',
        'MM': 'my',
        'MN': 'mn',
        'MO': 'zh_Hant',
        'MP': 'en',
        'MQ': 'fr',
        'MR': 'ar',
        'MS': 'en',
        'MT': 'mt',
        'MU': 'en',
        'MV': 'dv',
        'MW': 'ny',
        'MX': 'es',
        'MY': 'ms',
        'MZ': 'pt',
        'NA': 'en',
        'NC': 'fr',
        'NE': 'fr',
        'NF': 'en',
        'NG': 'en',
        'NI': 'es',
        'NL': 'nl',
        'NO': 'nb',
        'NP': 'ne',
        'NR': 'en',
        'NU': 'en',
        'NZ': 'en',
        'OM': 'ar',
        'PA': 'es',
        'PE': 'es',
        'PF': 'fr',
        'PG': 'tpi',
        'PH': 'en',
        'PK': 'ur',
        'PL': 'pl',
        'PM': 'fr',
        'PN': 'en',
        'PR': 'es',
        'PS': 'ar',
        'PT': 'pt',
        'PW': 'pau',
        'PY': 'gn',
        'QA': 'ar',
        'RE': 'fr',
        'RO': 'ro',
        'RS': 'sr',
        'RU': 'ru',
        'RW': 'rw',
        'SA': 'ar',
        'SB': 'en',
        'SC': 'fr',
        'SD': 'en',
        'SE': 'sv',
        'SG': 'en',
        'SH': 'en',
        'SI': 'sl',
        'SJ': 'nb',
        'SK': 'sk',
        'SL': 'en',
        'SM': 'it',
        'SN': 'wo',
        'SO': 'so',
        'SR': 'nl',
        'SS': 'en',
        'ST': 'pt',
        'SV': 'es',
        'SX': 'en',
        'SY': 'ar',
        'SZ': 'en',
        'TC': 'en',
        'TD': 'fr',
        'TG': 'fr',
        'TH': 'th',
        'TJ': 'tg',
        'TK': 'tkl',
        'TL': 'tet',
        'TM': 'tk',
        'TN': 'ar',
        'TO': 'to',
        'TR': 'tr',
        'TT': 'en',
        'TV': 'tvl',
        'TW': 'zh_Hant',
        'TZ': 'sw',
        'UA': 'uk',
        'UG': 'sw',
        'UM': 'en',
        'US': 'en',
        'UY': 'es',
        'UZ': 'uz',
        'VA': 'it',
        'VC': 'en',
        'VE': 'es',
        'VG': 'en',
        'VI': 'en',
        'VN': 'vi',
        'VU': 'bi',
        'WF': 'fr',
        'WS': 'sm',
        'YE': 'ar',
        'YT': 'fr',
        'ZA': 'en',
        'ZM': 'en',
        'ZW': 'sn',
    }

    # phone prefixes

    PHONE_PREFIXES = {
        'AW': 297,
        'AU': 61,
        'AT': 43,
        'AZ': 944,
        'BS': 1242,
        'BH': 973,
        'BD': 880,
        'BB': 1246,
        'BY': 375,
        'BE': 32,
        'BZ': 501,
        'BJ': 229,
        'BM': 1441,
        'BT': 975,
        'BA': 387,
        'BW': 267,
        'BR': 55,
        'BG': 359,
        'CA': 1,
        'CL': 56,
        'CN': 86,
        'CU': 53,
        'DK': 45,
        'EG': 20,
        'EE': 372,
        'FI': 358,
        'FR': 33,
        'DE': 49,
        'GR': 30,
        'HK': 852,
        'HU': 36,
        'IS': 354,
        'IN': 91,
        'ID': 62,
        'IR': 98,
        'IQ': 964,
        'IE': 353,
        'IL': 972,
        'IT': 39,
        'JM': 1876,
        'JP': 81,
        'LV': 371,
        'LI': 4175,
        'LT': 370,
        'LU': 352,
        'MG': 261,
        'MX': 52,
        'NL': 31,
        'NZ': 64,
        'NO': 47,
        'PE': 51,
        'PH': 63,
        'PL': 48,
        'PT': 351,
        'QA': 974,
        'RO': 7,
        'RU': 7,
        'SN': 221,
        'SG': 65,
        'SK': 421,
        'SI': 386,
        'ES': 34,
        'SE': 46,
        'CH': 41,
        'TH': 66,
        'TN': 216,
        'TR': 90,
        'UA': 380,
        'AE': 971,
        'GB': 44,
        'US': 1,
        'VE': 58,
        'VN': 84,
    }
