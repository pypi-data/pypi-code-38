# -*- coding: utf-8 -*-
import os
import re

from appconf import AppConf
from django.conf import settings as dj_settings
from django.core.cache import DEFAULT_CACHE_ALIAS
from django.utils.translation import gettext_lazy as _

settings = dj_settings


class CongoAppConf(AppConf):
    # sites

    SITE_MODEL = '' # eg 'maintenance.Site'

    # config

    CONFIG_CACHE_BACKEND = DEFAULT_CACHE_ALIAS

    # logs

    LOG_MODEL = '' # eg 'maintenance.Log'
    LOG_ROOT = os.path.join(settings.BASE_DIR, 'logs')
    COMMON_ERRORS_IGNORE_LIST = []
    COMMON_WARNINGS_IGNORE_LIST = [
        "ImportWarning: can't resolve package from __spec__ or __package__, falling back on __name__ and __path__",
    ]

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

    AUTHENTICATION_DOMAIN = settings.ALLOWED_HOSTS[0]
    SYSTEM_USER_ID = None

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
    EMAIL_TEMPLATE_DOMAIN = settings.ALLOWED_HOSTS[0] # domain used as placeholder in e-mail templates
    EMAIL_UNSUBSCRIBE_EMAIL = settings.DEFAULT_FROM_EMAIL # eg 'unsubscribe@example.com'
    EMAIL_UNSUBSCRIBE_URL_NAME = 'congo:email_unsubscribe'

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
        ('ECO', _("Losowy numer")),
    )
    SMS_BACKEND = 'congo.communication.backends.console.SMSBackend' # eg 'congo.communication.backends.smsapi.SMSBackend'

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

    DEFAULT_META_TITLE = "Congo 3 Project by Integree"
    DEFAULT_META_TITLE_DIVIDER = "-"
    APPEND_DEFAULT_TITLE = True
    DEFAULT_META_DESCRIPTION = "Tools for faster and more efficient Django application developing"
    DEFAULT_META_IMAGE = '/static/congo/img/django-congo.png'

    # message class

    MESSAGE_ALERT_CLASS = "alert-%s"
    MESSAGE_DISMISS_CLASS = "alert-dismissible"
    MESSAGE_FADE_CLASS = "fade in"
    MESSAGE_TEXT_CLASS = "text-%s"
    MESSAGE_ICON_CLASS = "mdi mdi-%s"
    MESSAGE_CSS_CLASS_MAP = {
        'debug': 'debug',
        'info': 'info',
        'success': 'success',
        'question': 'question',
        'warning': 'warning',
        'error': 'danger',
    }
    MESSAGE_CSS_ICON_CLASS_MAP = {
        'debug': 'information-outline',
        'info': 'information-outline',
        'success': 'check-circle-outline',
        'question': 'help-circle-outline',
        'warning': 'alert-circle-outline',
        'error': 'close-circle-outline',
    }

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
    PARLER_2_PO_DEFAULT_LANG = None
    PARLER_2_PO_APPS = []
    PARLER_2_PO_IGNORE_APPS = []
    PARLER_2_PO_IGNORE_APPS = []
    PARLER_2_PO_MODELS = []
    PARLER_2_PO_IGNORE_MODELS = []
    PARLER_2_PO_IGNORE_MODELS = []

    # countries

    # https://github.com/SmileyChris/django-countries/blob/master/django_countries/data.py#L46
    COUNTRIES = (
        ('AF', _("Afganistan")),
        ('AX', _("Wyspy Alandzkie")),
        ('AL', _("Albania")),
        ('DZ', _("Algeria")),
        ('AS', _("Samoa Amerykańskie")),
        ('AD', _("Andora")),
        ('AO', _("Angola")),
        ('AI', _("Anguilla")),
        ('AQ', _("Antarktyda")),
        ('AG', _("Antigua i Barbuda")),
        ('AR', _("Argentyna")),
        ('AM', _("Armenia")),
        ('AW', _("Aruba")),
        ('AU', _("Australia")),
        ('AT', _("Austria")),
        ('AZ', _("Azerbejdżan")),
        ('BS', _("Bahamy")),
        ('BH', _("Bahrajn")),
        ('BD', _("Bangladesz")),
        ('BB', _("Barbados")),
        ('BY', _("Białoruś")),
        ('BE', _("Belgia")),
        ('BZ', _("Belize")),
        ('BJ', _("Benin")),
        ('BM', _("Bermudy")),
        ('BT', _("Bhutan")),
        ('BO', _("Boliwia")),
        ('BQ', _("Bonaire, Sint Eustatius i Saba")),
        ('BA', _("Bośnia i Hercegowina")),
        ('BW', _("Botswana")),
        ('BV', _("Wyspa Bouveta")),
        ('BR', _("Brazylia")),
        ('IO', _("Brytyjskie Terytorium Oceanu Indyjskiego")),
        ('BN', _("Brunei")),
        ('BG', _("Bułgaria")),
        ('BF', _("Burkina Faso")),
        ('BI', _("Burundi")),
        ('CV', _("Republika Zielonego Przylądka")),
        ('KH', _("Kambodża")),
        ('CM', _("Kamerun")),
        ('CA', _("Kanada")),
        ('KY', _("Kajmany")),
        ('CF', _("Republika Środkowoafrykańska")),
        ('TD', _("Czad")),
        ('CL', _("Chile")),
        ('CN', _("Chiny")),
        ('CX', _("Wyspa Bożego Narodzenia")),
        ('CC', _("Wyspy Kokosowe")),
        ('CO', _("Kolumbia")),
        ('KM', _("Komory")),
        ('CD', _("Kongo")),
        ('CG', _("Kongo")),
        ('CK', _("Wyspy Cooka")),
        ('CR', _("Kostaryka")),
        ('CI', _("Wybrzeże Kości Słoniowej")),
        ('HR', _("Chorwacja")),
        ('CU', _("Kuba")),
        ('CW', _("Curaçao")),
        ('CY', _("Cypr")),
        ('CZ', _("Czechy")),
        ('DK', _("Dania")),
        ('DJ', _("Dżibuti")),
        ('DM', _("Dominika")),
        ('DO', _("Dominikana")),
        ('EC', _("Ekwador")),
        ('EG', _("Egipt")),
        ('SV', _("Salwador")),
        ('GQ', _("Gwinea Równikowa")),
        ('ER', _("Erytrea")),
        ('EE', _("Estonia")),
        ('ET', _("Etiopia")),
        ('FK', _("Falklandy")),
        ('FO', _("Wyspy Owcze")),
        ('FJ', _("Fidżi")),
        ('FI', _("Finlandia")),
        ('FR', _("Francja")),
        ('GF', _("Gujana Francuska")),
        ('PF', _("Polinezja Francuska")),
        ('TF', _("Francuskie Terytoria Południowe i Antarktyczne")),
        ('GA', _("Gabon")),
        ('GM', _("Gambia")),
        ('GE', _("Gruzja")),
        ('DE', _("Niemcy")),
        ('GH', _("Ghana")),
        ('GI', _("Gibraltar")),
        ('GR', _("Grecja")),
        ('GL', _("Grenlandia")),
        ('GD', _("Grenada")),
        ('GP', _("Gwadelupa")),
        ('GU', _("Guam")),
        ('GT', _("Gwatemala")),
        ('GG', _("Guernsey")),
        ('GN', _("Gwinea")),
        ('GW', _("Gwinea Bissa")),
        ('GY', _("Gujana")),
        ('HT', _("Haiti")),
        ('HM', _("Wyspy Heard i McDonalda")),
        ('VA', _("Watykan")),
        ('HN', _("Honduras")),
        ('HK', _("Hongkong")),
        ('HU', _("Węgry")),
        ('IS', _("Islandia")),
        ('IN', _("Indie")),
        ('ID', _("Indonezja")),
        ('IR', _("Iran")),
        ('IQ', _("Irak")),
        ('IE', _("Irlandia")),
        ('IM', _("Wyspa Man")),
        ('IL', _("Izrael")),
        ('IT', _("Włochy")),
        ('JM', _("Jamajka")),
        ('JP', _("Japonia")),
        ('JE', _("Jersey")),
        ('JO', _("Jordania")),
        ('KZ', _("Kazachstan")),
        ('KE', _("Kenia")),
        ('KI', _("Kiribati")),
        ('KP', _("Korea Północna")),
        ('KR', _("Korea Południowa")),
        ('KW', _("Kuwejt")),
        ('KG', _("Kirgistan")),
        ('LA', _("Laos")),
        ('LV', _("Łotwa")),
        ('LB', _("Liban")),
        ('LS', _("Lesotho")),
        ('LR', _("Liberia")),
        ('LY', _("Libia")),
        ('LI', _("Liechtenstein")),
        ('LT', _("Litwa")),
        ('LU', _("Luksemburg")),
        ('MO', _("Maka")),
        ('MK', _("Macedonia")),
        ('MG', _("Madagaskar")),
        ('MW', _("Malawi")),
        ('MY', _("Malezja")),
        ('MV', _("Malediwy")),
        ('ML', _("Mali")),
        ('MT', _("Malta")),
        ('MH', _("Wyspy Marshalla")),
        ('MQ', _("Martynika")),
        ('MR', _("Mauretania")),
        ('MU', _("Mauritius")),
        ('YT', _("Majotta")),
        ('MX', _("Meksyk")),
        ('FM', _("Mikronezja")),
        ('MD', _("Mołdawia")),
        ('MC', _("Monako")),
        ('MN', _("Mongolia")),
        ('ME', _("Czarnogóra")),
        ('MS', _("Montserrat")),
        ('MA', _("Maroko")),
        ('MZ', _("Mozambik")),
        ('MM', _("Mjanma")),
        ('NA', _("Namibia")),
        ('NR', _("Naur")),
        ('NP', _("Nepal")),
        ('NL', _("Holandia")),
        ('NC', _("Nowa Kaledonia")),
        ('NZ', _("Nowa Zelandia")),
        ('NI', _("Nikaragua")),
        ('NE', _("Niger")),
        ('NG', _("Nigeria")),
        ('NU', _("Niue")),
        ('NF', _("Norfolk")),
        ('MP', _("Mariany Północne")),
        ('NO', _("Norwegia")),
        ('OM', _("Oman")),
        ('PK', _("Pakistan")),
        ('PW', _("Pala")),
        ('PS', _("Palestyna")),
        ('PA', _("Panama")),
        ('PG', _("Papua-Nowa Gwinea")),
        ('PY', _("Paragwaj")),
        ('PE', _("Per")),
        ('PH', _("Filipiny")),
        ('PN', _("Pitcairn")),
        ('PL', _("Polska")),
        ('PT', _("Portugalia")),
        ('PR', _("Portoryko")),
        ('QA', _("Katar")),
        ('RE', _("Reunion")),
        ('RO', _("Rumunia")),
        ('RU', _("Rosja")),
        ('RW', _("Rwanda")),
        ('BL', _("Saint-Barthélemy")),
        ('SH', _("Wyspa Świętej Heleny, Wyspa Wniebowstąpienia i Tristan da Cunha")),
        ('KN', _("Saint Kitts i Nevis")),
        ('LC', _("Saint Lucia")),
        ('MF', _("Saint-Martin")),
        ('PM', _("Saint-Pierre i Miquelon")),
        ('VC', _("Saint Vincent i Grenadyny")),
        ('WS', _("Samoa")),
        ('SM', _("San Marino")),
        ('ST', _("Wyspy Świętego Tomasza i Książęca")),
        ('SA', _("Arabia Saudyjska")),
        ('SN', _("Senegal")),
        ('RS', _("Serbia")),
        ('SC', _("Seszele")),
        ('SL', _("Sierra Leone")),
        ('SG', _("Singapur")),
        ('SX', _("Sint Maarten")),
        ('SK', _("Słowacja")),
        ('SI', _("Słowenia")),
        ('SB', _("Wyspy Salomona")),
        ('SO', _("Somalia")),
        ('ZA', _("Republika Południowej Afryki")),
        ('GS', _("Georgia Południowa i Sandwich Południowy")),
        ('SS', _("Sudan Południowy")),
        ('ES', _("Hiszpania")),
        ('LK', _("Sri Lanka")),
        ('SD', _("Sudan")),
        ('SR', _("Surinam")),
        ('SJ', _("Svalbard i Jan Mayen")),
        ('SZ', _("Suazi")),
        ('SE', _("Szwecja")),
        ('CH', _("Szwajcaria")),
        ('SY', _("Syria")),
        ('TW', _("Tajwan")),
        ('TJ', _("Tadżykistan")),
        ('TZ', _("Tanzania")),
        ('TH', _("Tajlandia")),
        ('TL', _("Timor Wschodni")),
        ('TG', _("Togo")),
        ('TK', _("Tokela")),
        ('TO', _("Tonga")),
        ('TT', _("Trynidad i Tobago")),
        ('TN', _("Tunezja")),
        ('TR', _("Turcja")),
        ('TM', _("Turkmenistan")),
        ('TC', _("Turks i Caicos")),
        ('TV', _("Tuval")),
        ('UG', _("Uganda")),
        ('UA', _("Ukraina")),
        ('AE', _("Zjednoczone Emiraty Arabskie")),
        ('GB', _("Wielka Brytania")),
        ('UM', _("Dalekie Wyspy Mniejsze Stanów Zjednoczonych")),
        ('US', _("Stany Zjednoczone Ameryki")),
        ('UY', _("Urugwaj")),
        ('UZ', _("Uzbekistan")),
        ('VU', _("Vanuat")),
        ('VE', _("Wenezuela")),
        ('VN', _("Wietnam")),
        ('VG', _("Brytyjskie Wyspy Dziewicze")),
        ('VI', _("Wyspy Dziewicze Stanów Zjednoczonych")),
        ('WF', _("Wallis i Futuna")),
        ('EH', _("Sahara Zachodnia")),
        ('YE', _("Jemen")),
        ('ZM', _("Zambia")),
        ('ZW', _("Zimbabwe")),
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
