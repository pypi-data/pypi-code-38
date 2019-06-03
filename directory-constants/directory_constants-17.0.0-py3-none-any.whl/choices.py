import json
from operator import itemgetter
import os

from directory_constants import cms, expertise, sectors


INDUSTRIES = (
    (sectors.AEROSPACE, 'Aerospace'),
    (sectors.ADVANCED_MANUFACTURING, 'Advanced manufacturing'),
    (sectors.AIRPORTS, 'Airports'),
    (
        sectors.AGRICULTURE_HORTICULTURE_AND_FISHERIES,
        'Agriculture, horticulture and fisheries'
    ),
    (sectors.AUTOMOTIVE, 'Automotive'),
    (
        sectors.BIOTECHNOLOGY_AND_PHARMACEUTICALS,
        'Biotechnology and pharmaceuticals'
    ),
    (
        sectors.BUSINESS_AND_CONSUMER_SERVICES,
        'Business and consumer services'
    ),
    (sectors.CHEMICALS, 'Chemicals'),
    (
        sectors.CLOTHING_FOOTWEAR_AND_FASHION,
        'Clothing, footwear and fashion'),
    (sectors.COMMUNICATIONS, 'Communications'),
    (sectors.CONSTRUCTION, 'Construction'),
    (sectors.CREATIVE_AND_MEDIA, 'Creative and media'),
    (sectors.EDUCATION_AND_TRAINING, 'Education and training'),
    (sectors.ELECTRONICS_AND_IT_HARDWARE, 'Electronics and IT hardware'),
    (sectors.ENVIRONMENT, 'Environment'),
    (
        sectors.FINANCIAL_AND_PROFESSIONAL_SERVICES,
        'Financial and professional services'
    ),
    (sectors.FOOD_AND_DRINK, 'Food and drink'),
    (
        sectors.GIFTWARE_JEWELLERY_AND_TABLEWARE,
        'Giftware, jewellery and tableware'
    ),
    (sectors.GLOBAL_SPORTS_INFRASTRUCTURE, 'Global sports infrastructure'),
    (sectors.HEALTHCARE_AND_MEDICAL, 'Healthcare and medical'),
    (
        sectors.HOUSEHOLD_GOODS_FURNITURE_AND_FURNISHINGS,
        'Household goods, furniture and furnishings'
    ),
    (sectors.LIFE_SCIENCES, 'Life sciences'),
    (sectors.LEISURE_AND_TOURISM, 'Leisure and tourism'),
    (sectors.LEGAL_SERVICES, 'Legal services'),
    (sectors.MARINE, 'Marine'),
    (
        sectors.MECHANICAL_ELECTRICAL_AND_PROCESS_ENGINEERING,
        'Mechanical electrical and process engineering'
    ),
    (sectors.METALLURGICAL_PROCESS_PLANT, 'Metallurgical process plant'),
    (
        sectors.METALS_MINERALS_AND_MATERIALS,
        'Metals, minerals and materials'
    ),
    (sectors.MINING, 'Mining'),
    (sectors.OIL_AND_GAS, 'Oil and gas'),
    (sectors.PORTS_AND_LOGISTICS, 'Ports and logistics'),
    (sectors.POWER, 'Power'),
    (sectors.RAILWAYS, 'Railways'),
    (sectors.RENEWABLE_ENERGY, 'Renewable energy'),
    (sectors.RETAIL_AND_LUXURY, 'Retail and luxury'),
    (sectors.SECURITY, 'Security'),
    (
        sectors.SOFTWARE_AND_COMPUTER_SERVICES,
        'Software and computer services'
    ),
    (
        sectors.TEXTILES_INTERIOR_TEXTILES_AND_CARPETS,
        'Textiles, interior textiles and carpets'
    ),
    (sectors.WATER, 'Water'),
)

EMPLOYEES = (
    ('1-10', '1-10'),
    ('11-50', '11-50'),
    ('51-200', '51-200'),
    ('201-500', '201-500'),
    ('501-1000', '501-1,000'),
    ('1001-10000', '1,001-10,000'),
    ('10001+', '10,001+'),
)

CMS_APP_CHOICES = [
    (cms.FIND_A_SUPPLIER, 'Find a Supplier'),
    (cms.EXPORT_READINESS, 'Export Readiness'),
    (cms.INVEST, 'Invest'),
    (cms.COMPONENTS, 'Components'),
    (cms.GREAT_INTERNATIONAL, 'Great International')
]


CONTACT_OPTIONS = (
    ('EMAIL', 'Email'),
    ('PHONE', 'Phone'),
)

EXPERTISE_LANGUAGES = [
    ('ab', 'Abkhazian'),
    ('aa', 'Afar'),
    ('af', 'Afrikaans'),
    ('ak', 'Akan'),
    ('sq', 'Albanian'),
    ('am', 'Amharic'),
    ('ar', 'Arabic'),
    ('an', 'Aragonese'),
    ('hy', 'Armenian'),
    ('as', 'Assamese'),
    ('av', 'Avaric'),
    ('ay', 'Aymara'),
    ('az', 'Azerbaijani'),
    ('bm', 'Bambara'),
    ('ba', 'Bashkir'),
    ('eu', 'Basque'),
    ('be', 'Belarusian'),
    ('bn', 'Bengali'),
    ('bi', 'Bislama'),
    ('bs', 'Bosnian'),
    ('br', 'Breton'),
    ('bg', 'Bulgarian'),
    ('my', 'Burmese'),
    ('yue', 'Cantonese'),
    ('ca', 'Catalan'),
    ('km', 'Central Khmer'),
    ('ce', 'Chechen'),
    ('zh', 'Chinese (written, simplified)'),
    ('kw', 'Cornish'),
    ('co', 'Corsican'),
    ('cr', 'Cree'),
    ('hr', 'Croatian'),
    ('cs', 'Czech'),
    ('da', 'Danish'),
    ('dv', 'Divehi; Dhivehi; Maldivian'),
    ('nl', 'Dutch; Flemish'),
    ('dz', 'Dzongkha'),
    ('en', 'English'),
    ('et', 'Estonian'),
    ('ee', 'Ewe'),
    ('fo', 'Faroese'),
    ('fj', 'Fijian'),
    ('fi', 'Finnish'),
    ('fr', 'French'),
    ('ff', 'Fulah'),
    ('gd', 'Gaelic'),
    ('gl', 'Galician'),
    ('lg', 'Ganda'),
    ('ka', 'Georgian'),
    ('de', 'German'),
    ('el', 'Greek'),
    ('gn', 'Guarani'),
    ('gu', 'Gujarati'),
    ('ht', 'Haitian; Haitian Creole'),
    ('ha', 'Hausa'),
    ('he', 'Hebrew'),
    ('hz', 'Herero'),
    ('hi', 'Hindi'),
    ('ho', 'Hiri Motu'),
    ('hu', 'Hungarian'),
    ('is', 'Icelandic'),
    ('ig', 'Igbo'),
    ('id', 'Indonesian'),
    ('ik', 'Inupiaq'),
    ('ga', 'Irish'),
    ('it', 'Italian'),
    ('ja', 'Japanese'),
    ('jv', 'Javanese'),
    ('kn', 'Kannada'),
    ('kr', 'Kanuri'),
    ('ks', 'Kashmiri'),
    ('kk', 'Kazakh'),
    ('ki', 'Kikuyu; Gikuyu'),
    ('rw', 'Kinyarwanda'),
    ('ky', 'Kirghiz; Kyrgyz'),
    ('kv', 'Komi'),
    ('kg', 'Kongo'),
    ('ko', 'Korean'),
    ('kj', 'Kuanyama; Kwanyama'),
    ('ku', 'Kurdish'),
    ('lo', 'Lao'),
    ('lv', 'Latvian'),
    ('li', 'Limburgan; Limburger; Limburgish'),
    ('ln', 'Lingala'),
    ('lt', 'Lithuanian'),
    ('lu', 'Luba-Katanga'),
    ('lb', 'Luxembourgish; Letzeburgesch'),
    ('mk', 'Macedonian'),
    ('mg', 'Malagasy'),
    ('ms', 'Malay'),
    ('ml', 'Malayalam'),
    ('mt', 'Maltese'),
    ('gv', 'Manx'),
    ('cmn', 'Mandarin'),
    ('mi', 'Maori'),
    ('mr', 'Marathi'),
    ('mh', 'Marshallese'),
    ('mn', 'Mongolian'),
    ('na', 'Nauru'),
    ('ng', 'Ndonga'),
    ('ne', 'Nepali'),
    ('se', 'Northern Sami'),
    ('no', 'Norwegian'),
    ('oj', 'Ojibwa'),
    ('or', 'Oriya'),
    ('om', 'Oromo'),
    ('os', 'Ossetian; Ossetic'),
    ('pa', 'Panjabi; Punjabi'),
    ('fa', 'Persian'),
    ('pl', 'Polish'),
    ('pt', 'Portuguese'),
    ('ps', 'Pushto; Pashto'),
    ('qu', 'Quechua'),
    ('ro', 'Romanian; Moldavian; Moldovan'),
    ('rm', 'Romansh'),
    ('rn', 'Rundi'),
    ('ru', 'Russian'),
    ('sm', 'Samoan'),
    ('sg', 'Sango'),
    ('sc', 'Sardinian'),
    ('sr', 'Serbian'),
    ('sn', 'Shona'),
    ('ii', 'Sichuan Yi; Nuosu'),
    ('sd', 'Sindhi'),
    ('si', 'Sinhala; Sinhalese'),
    ('sk', 'Slovak'),
    ('sl', 'Slovenian'),
    ('so', 'Somali'),
    ('st', 'Sotho, Southern'),
    ('es', 'Spanish'),
    ('su', 'Sundanese'),
    ('sw', 'Swahili'),
    ('ss', 'Swati'),
    ('sv', 'Swedish'),
    ('ty', 'Tahitian'),
    ('tg', 'Tajik'),
    ('ta', 'Tamil'),
    ('tt', 'Tatar'),
    ('te', 'Telugu'),
    ('th', 'Thai'),
    ('bo', 'Tibetan'),
    ('ti', 'Tigrinya'),
    ('to', 'Tonga (Tonga Islands)'),
    ('ts', 'Tsonga'),
    ('tn', 'Tswana'),
    ('tr', 'Turkish'),
    ('tk', 'Turkmen'),
    ('tw', 'Twi'),
    ('ug', 'Uighur; Uyghur'),
    ('uk', 'Ukrainian'),
    ('ur', 'Urdu'),
    ('uz', 'Uzbek'),
    ('ve', 'Venda'),
    ('vi', 'Vietnamese'),
    ('wa', 'Walloon'),
    ('cy', 'Welsh'),
    ('yi', 'Yiddish'),
    ('yo', 'Yoruba'),
    ('za', 'Zhuang; Chuang'),
    ('zu', 'Zulu'),
]


EU_COUNTRIES = {
    'AT': 'Austria',
    'BE': 'Belgium',
    'BG': 'Bulgaria',
    'HR': 'Croatia',
    'CY': 'Cyprus',
    'CZ': 'Czechia',
    'DK': 'Denmark',
    'EE': 'Estonia',
    'FI': 'Finland',
    'FR': 'France',
    'DE': 'Germany',
    'GR': 'Greece',
    'HU': 'Hungary',
    'IE': 'Ireland',
    'IT': 'Italy',
    'LV': 'Latvia',
    'LT': 'Lithuania',
    'LU': 'Luxembourg',
    'MT': 'Malta',
    'NL': 'Netherlands',
    'PL': 'Poland',
    'PT': 'Portugal',
    'RO': 'Romania',
    'SK': 'Slovakia',
    'SI': 'Slovenia',
    'ES': 'Spain',
    'SE': 'Sweden'
}

EXPERTISE_REGION_CHOICES = [
    ('NORTH_EAST', 'North East'),
    ('NORTH_WEST', 'North West'),
    ('NORTHERN_IRELAND', 'Northern Ireland'),
    ('YORKSHIRE_AND_HUMBER', 'Yorkshire and the Humber'),
    ('EAST_MIDLANDS', 'East Midlands'),
    ('WEST_MIDLANDS', 'West Midlands'),
    ('EASTERN', 'East of England'),
    ('LONDON', 'London'),
    ('SOUTH_EAST', 'South East'),
    ('SOUTH_WEST', 'South West'),
    ('SCOTLAND', 'Scotland'),
    ('WALES', 'Wales'),
]

EXPERTISE_FINANCIAL = [(i, i) for i in expertise.FINANCIAL]

EXPERTISE_MANAGEMENT_CONSULTING = [
    (i, i) for i in expertise.MANAGEMENT_CONSULTING
]

EXPERTISE_HUMAN_RESOURCES = [(i, i) for i in expertise.HUMAN_RESOURCES]

EXPERTISE_LEGAL = [(i, i) for i in expertise.LEGAL]

EXPERTISE_PUBLICITY = [(i, i) for i in expertise.PUBLICITY]

EXPERTISE_BUSINESS_SUPPORT = [(i, i) for i in expertise.BUSINESS_SUPPORT]

LEAD_GENERATION_EXPORT_DESTINATIONS = (
    ('CN', 'China'),
    ('DE', 'Germany'),
    ('IN', 'India'),
    ('JP', 'Japan'),
    ('US', 'United States'),
)


# from https://www.registers.service.gov.uk/registers/country
country_fixture_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), './fixtures/country.json'
)
with open(country_fixture_path, 'r') as f:
    COUNTRY_CHOICES = []
    for country in json.loads(f.read()).values():
        for item in country['item']:
            if 'end-date' not in item:
                COUNTRY_CHOICES.append((item['country'], item['name']))
    COUNTRY_CHOICES.sort(key=itemgetter(1))
