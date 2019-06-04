import os
import subprocess
import shlex
import shutil
import uuid
import gzip
import datetime
import pandas as pd
import re
import botocore
import dateutil.parser

from boto3.dynamodb.conditions import Key
from decimal import Decimal
from geopy.location import Point
from geopy.geocoders import Nominatim

from collections import MutableMapping
# from itertools import islice

from metagenomi.logger import logger
from metagenomi.db import (S3resource, S3)
from metagenomi.config import (TIME_FMT, DECIMAL_ROUNDING)
from metagenomi.mgvalidator import MgValidator
# from metagenomi.models.sample import Sample


def generate_mgid(project, loc, source, type, db):
    c = 1
    mgid = f'{project}_{c:04d}_{loc}_{source}-{type}'
    while in_db(mgid, db):
        c += 1
        mgid = f'{project}_{c:04d}_{loc}_{source}-{type}'

    print(f'Generated mgid {mgid}')
    return mgid


def window(fseq, window_size=5):
    for i in range(len(fseq) - window_size + 1):
        yield fseq[i:i+window_size]


def find_mgid(path):
    for i in window(path, 22):
        if is_mgid(i):
            return i
    return None


def is_mgid(putative_mgid, raise_error=False):
    schema = {'mgid': {'type': 'mgid', 'required': True}}
    v = MgValidator(schema)
    if v.validate({'mgid': putative_mgid}):
        return True
    else:
        if raise_error:
            raise(ValueError(v.errors))
        return False


def check_s3file(file):
    # LOAD works better than HEAD
    # Check if a specific key (object) exists
    try:
        bucket = file.split('/')[2]
        key = '/'.join(file.split('/')[3:])
    except IndexError:
        return False

    try:
        S3resource.Object(bucket, key).load()
    except botocore.exceptions.ClientError:
        return False
    return True


def check_s3path(path):
    try:
        bucket = path.split('/')[2]
        key = '/'.join(path.split('/')[3:])
    except IndexError:
        return False

    result = S3.list_objects(Bucket=bucket, Prefix=key)
    if 'Contents' in result:
        return True
    return False


def get_file_size(f):
    bucket = f.split('/')[2]
    key = '/'.join(f.split('/')[3:])

    response = S3.head_object(Bucket=bucket, Key=key)
    size = response['ContentLength']
    return int(size)


def in_db(mgid, db):
    response = db.table.query(
                        KeyConditionExpression=Key('mgid').eq(mgid)
                        )
    if len(response['Items']) < 1:
        return False
    else:
        return True


def altid_in_db(alt_id, db, return_mgid=True):
    response = db.table.query(
        IndexName='alt_id-mgproject-index',
        KeyConditionExpression=Key('alt_id').eq(alt_id))

    if len(response['Items']) < 1:
        return False
    else:
        if return_mgid:
            mgid = response['Items'][0]['mgid']
            return mgid
        return True


def rchop(thestring, ending):
    '''
    Chop an extension.
    :param thestring: filepath string
    :param ending: extension. Include '.'
    :return: filepath - extension, if the filepath ends with the extension.
    '''
    if thestring.endswith(ending):
        return thestring[:-len(ending)]
    return thestring


def unzip(filename, extension='.gz'):
    '''
    Unzip a file with a given extension if it has that extension.
    :param filename: filepath string
    :param extension: extension to check for
    '''
    if filename == rchop(filename, extension):
        return filename
    else:
        outfile = rchop(filename, extension)
        with gzip.open(filename, 'rb') as f_in:
            with open(outfile, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            return outfile


def basename(full_name, extensions=[]):
    '''
    Return basename of a path-like string. Works like shell basename with
    extensions.
    :param full_name: full path to perform basename on
    :param ext: array of extensionto remove, if required
    :return: string of the basename
    '''
    bname = full_name.split('/')[-1]
    if len(extensions) > 0:
        for ext in extensions:
            if bname.endswith(ext):
                return(bname[:-len(ext)])
    return(bname)


def download_folder(s3_path, dir_to_dl, dry_run=False):
    '''
    Downloads a folder from s3
    :param s3_path: s3 folder path
    :param dir_to_dl: local path of dir to download to
    :return: dir that was downloaded
    '''

    cmd = f'aws s3 cp --recursive {s3_path} {dir_to_dl}'

    if dry_run:
        print(cmd)
    else:
        subprocess.check_call(shlex.split(cmd))

    return dir_to_dl


def download_file_multi(s3_path_list, dir_to_dl, dry_run=False):
    print(f's3_path_list \n\n{s3_path_list}')
    '''
    Downloads multiple files from s3
    :param s3_path_list: list of s3 object paths
    :param dir_to_dl: local path of dir to download to
    :return: list of local file paths of the downloaded objects
    '''
    local_paths = list()

    seen = dict()
    dupnum = 1
    for s3_path in s3_path_list:
        key = '/'.join(s3_path.split('/')[3:])
        name = key.split('/')[-1]
        if name in seen:
            name = f'{dupnum}_{name}'
            dupnum += 1
        else:
            seen[name] = 1
        local_paths.append(download_file_as(s3_path, dir_to_dl, name, dry_run))

    return(local_paths)


def download_file(s3_path, dir_to_dl, dry_run=False, overwrite=True):
    '''
    Downloads a folder from s3
    :param s3_path: s3 object path
    :param dir_to_dl: local path of dir to download to
    :return: local file path of the object downloaded
    '''
    bucket = s3_path.split('/')[2]
    key = '/'.join(s3_path.split('/')[3:])

    object_name = key.split('/')[-1]
    local_file_name = os.path.join(dir_to_dl, object_name)
    if overwrite is False and os.path.isfile(local_file_name):
        return local_file_name

    if dry_run:
        print('Fake download')
    else:
        print(f'bucket {bucket} key {key} local_file_name {local_file_name}')
        S3resource.Object(bucket, key).download_file(local_file_name)
    return local_file_name


def download_file_as(s3_path, dir_to_dl, name, dry_run=False):
    '''
    Downloads a folder from s3 and change its local name
    :param s3_path: s3 object path
    :param dir_to_dl: local path of dir to download to
    :param name: name of file to create
    :return: local file path of the object downloaded
    '''
    bucket = s3_path.split('/')[2]
    key = '/'.join(s3_path.split('/')[3:])

    local_file_name = os.path.join(dir_to_dl, name)

    if dry_run:
        print('Fake download')
    else:
        print(f'bucket {bucket} key {key} local_file_name {local_file_name}')
        S3resource.Object(bucket, key).download_file(local_file_name)
    return local_file_name


def download_pattern(s3_path,
                     dir_to_dl,
                     include,
                     exclude='"*"',
                     dry_run=False):
    '''
    Downloads multiple files from s3 based on include/exclude
    :param s3_path: s3 object path
    :param dir_to_dl: local path of dir to download to
    :return: local path of dir to download to
    '''

    # check include and exclude to be sure they start and end with with ""
    if include[0] != '"':
        if include[-1] != '"':
            include = f'"{include}"'

    dir_to_dl = dir_to_dl.rstrip('/')+'/'

    bucket = s3_path.split('/')[2]
    key = '/'.join(s3_path.split('/')[3:])

    cmd = f"aws s3 cp --recursive --exclude={exclude} --include={include}"
    cmd += f" s3://{bucket}/{key} {dir_to_dl}"

    if dry_run:
        print('--- dry run ---')
        print(cmd)

    else:
        subprocess.check_call(shlex.split(cmd))

    return dir_to_dl


def rm_files(s3_path, files, dry_run=False):
    '''
    Removes files fiven an s3 path and a list of filenames
    :param s3_path: s3 object path
    :param files: list format of file names
    :return: nothing
    '''

    bucket = s3_path.split('/')[2]
    key = '/'.join(s3_path.split('/')[3:])

    for f in files:
        cmd = f'aws s3 rm s3://{bucket}/{key}/{f}'

        if dry_run:
            print('--- dry run ---')
            print(cmd)

        else:
            subprocess.check_call(shlex.split(cmd))


def upload_folder(s3_path, local_folder_path, dry_run=False):
    '''
    Uploads a folder to s3
    :param s3_path: s3 path to upload folder to
    :param local_folder_path: path to local folder
    '''

    cmd = f'aws s3 cp --recursive {local_folder_path} {s3_path}'

    if dry_run:
        print(cmd)
    else:
        subprocess.check_call(shlex.split(cmd))


def upload_file(local_path, s3_path, compress=False, dry_run=False):
    '''
    Uploads a file to s3
    :param local_path: path to local file
    :param s3_path: s3 path to object
    :param compress: compress before uploading?
    :param dry_run: dry run only
    :return: response from the upload file call
    '''
    bucket = s3_path.split('/')[2]
    key = '/'.join(s3_path.split('/')[3:])

    if compress:
        subprocess.check_call(['pigz', local_path])
        local_path += '.gz'

    if dry_run:
        print('Fake upload')
    else:
        response = S3resource.Object(bucket, key).upload_file(local_path)
        return response


def generate_working_dir(working_dir_base):
    '''
    Creates a unique working dir to prevent overwrites from multiple containers
    :param working_dir_base: base working dir (e.g. /scratch)
    :return: a uniquely-named subfolder in working_dir_base with a uuid
    '''

    working_dir = os.path.join(working_dir_base, str(uuid.uuid4()))
    # try to make the dir
    try:
        os.mkdir(working_dir)
    except Exception as e:
        # already exists
        logger.debug(e)
        return working_dir_base
    return working_dir


def delete_working_dir(working_dir):
    '''
    Delete the working dir
    :param working_dir: working directory
    '''

    try:
        shutil.rmtree(working_dir)
    except Exception as e:
        logger.debug(e)
        print(f"Can't delete {working_dir}")


def get_time():
    '''
    Returns current timestamp in human readable format
    '''
    return str(datetime.datetime.now().strftime(TIME_FMT))


def to_decimal(d, c=[], skipstr=False):
    '''
    convert values from input dict - or scalar - to decimal; if value is a
    dict, recursively call to_decimal() to convert nested values into
    decimals

    If is a pandas DataFrame, convert the given columns to decimals
    If it is a list, can optionally skip strings in the list. Otherwise
    converts to ints of int or to decimal.
    '''

    if isinstance(d, pd.DataFrame):
        for i in c:
            d[i] = [round(Decimal(i), DECIMAL_ROUNDING) for i in d[i]]
        return d

    if d == 'None' or d == 'NA' or d == 'none' or d == '' or d == 'nan' or d is None:
        return 'None'

    if isinstance(d, str):
        if skipstr is True:
            return d
        else:
            d = re.sub("\D", "", d)

    if isinstance(d, int):
        return int(d)

    if isinstance(d, dict):
        new_di = dict()
        for k, v in d.items():
            if isinstance(v, dict):
                to_decimal(v, new_di)
            if isinstance(v, float):
                new_di[k] = round(Decimal(v), DECIMAL_ROUNDING)
            else:
                new_di[k] = v

            if isinstance(v, list):
                new_di[k] = [to_decimal(i, skipstr=True) for i in v]

        return new_di

    else:
        return round(Decimal(d), DECIMAL_ROUNDING)


def to_datetime(d):
    '''
    UPDTAED MAY 8th: MAY BREAK THINGS
    '''

    if d == 'not applicable' or d == 'None' or d is None or d == 'NA' or d == 'missing':
        return 'None'
    try:
        dt = dateutil.parser.parse(d)
        # datetime.datetime.strptime(d, TIME_FMT)
        return str(dt.strftime(TIME_FMT))

    except ValueError:
        raise ValueError(f'Could not convert {d} to a datetime')


def to_latlon(latlon, country=None):
    '''
    64° 1’ 7” N, 21° 11’ 20” W -->

    '''
    latlon = latlon.replace('”', 's')
    latlon = latlon.replace("’", 'm')

    try:
        p = Point(latlon)
        return f'{p[0]}, {p[1]}'

    except ValueError as e:
        if country:
            geolocator = Nominatim(user_agent="test")
            try:
                loc = geolocator.geocode(country)
                return(f'{loc.latitude}, {loc.longitude}')
            except AttributeError:
                print(e)
    return 'None'


def to_int(d, columns=[]):
    '''
    convert values from input pandas dataframe to int. Will not force
    conversion, will only convert the ones that can be converted.

    DOES NOT handle errors
    '''

    if isinstance(d, pd.DataFrame):
        for c in columns:
            d[c] = [int(i) for i in d[c]]

        return d

    if d == 'None' or d == 'NA' or d == 'none' or d == '' or d == 'nan' or d is None:
        return 'None'

    if isinstance(d, str):
        d = re.sub("\D", "", d)

    return int(d)


def delete_keys_from_dict(dictionary, keys):
    '''
    Removes keys from a nested dictionary INCLUDING lists of dictionaries
    '''

    keys_set = set(keys)  # an optimization for the "if key in keys" lookup

    modified_dict = {}
    for key, value in dictionary.items():
        if key not in keys_set:
            if isinstance(value, MutableMapping):
                modified_dict[key] = delete_keys_from_dict(value, keys_set)
            elif isinstance(value, list) and len(value) > 0:
                # only go into lists with dictionary items
                if isinstance(value[0], MutableMapping):
                    modified_dict[key] = []
                    for i in value:
                        if isinstance(i, MutableMapping):
                            modified_dict[key] += [delete_keys_from_dict(i, keys_set)]
                else:
                    modified_dict[key] = value
            else:
                modified_dict[key] = value  # or copy.deepcopy(value) if a copy is desired for non-dicts.
    return modified_dict


def delete_association(dictionary, association):
    '''
    Given a propely formated associated dictionary, remove the requested
    association.
    EXAMPLE
    d = {'assembly': ['a','b']}
    delete_association(d, 'a')
    {'assembly': ['b']}
    '''
    newd = {}
    for k, v in dictionary.items():
        newv = []
        for i in v:
            if i != association:
                newv.append(i)
        if len(newv) < 1:
            newv = ['None']
        newd[k] = newv
    return newd


def get_country_codes(inverted=False):
    '''
    :return: Dictionary of countries / regions and their 3-letter codes
    '''
    d = {
        "Afghanistan": "AFG",
        "Albania": "ALB",
        "Algeria": "DZA",
        "American Samoa": "ASM",
        "Andorra": "AND",
        "Angola": "AGO",
        "Anguilla": "AIA",
        "Antarctica": "ATA",
        "Antigua and Barbuda": "ATG",
        "Argentina": "ARG",
        "Armenia": "ARM",
        "Aruba": "ABW",
        "Australia": "AUS",
        "Austria": "AUT",
        "Azerbaijan": "AZE",
        "Bahamas": "BHS",
        "Bahrain": "BHR",
        "Bangladesh": "BGD",
        "Barbados": "BRB",
        "Belarus": "BLR",
        "Belgium": "BEL",
        "Belize": "BLZ",
        "Benin": "BEN",
        "Bermuda": "BMU",
        "Bhutan": "BTN",
        "Bolivia": "BOL",
        "Bonaire": "BES",
        "Bosnia and Herzegovina": "BIH",
        "Botswana": "BWA",
        "Bouvet Island": "BVT",
        "Brazil": "BRA",
        "British Indian Ocean Territory": "IOT",
        "Brunei Darussalam": "BRN",
        "Bulgaria": "BGR",
        "Burkina Faso": "BFA",
        "Burundi": "BDI",
        "Cambodia": "KHM",
        "Cameroon": "CMR",
        "Canada": "CAN",
        "Cape Verde": "CPV",
        "Cayman Islands": "CYM",
        "Central African Republic": "CAF",
        "Chad": "TCD",
        "Chile": "CHL",
        "China": "CHN",
        "Christmas Island": "CXR",
        "Cocos (Keeling) Islands": "CCK",
        "Colombia": "COL",
        "Comoros": "COM",
        "Congo": "COG",
        "Democratic Republic of the Congo": "COD",
        "Cook Islands": "COK",
        "Costa Rica": "CRI",
        "Croatia": "HRV",
        "Cuba": "CUB",
        "Curacao": "CUW",
        "Cyprus": "CYP",
        "Czech Republic": "CZE",
        "Cote d'Ivoire": "CIV",
        "Denmark": "DNK",
        "Djibo uti": "DJI",
        "Dominica": "DMA",
        "Dominican Republic": "DOM",
        "Ecuador": "ECU",
        "Egypt": "EGY",
        "El Salvador": "SLV",
        "Equatorial Guinea": "GNQ",
        "Eritrea": "ERI",
        "Estonia": "EST",
        "Ethiopia": "ETH",
        "Falkland Islands (Malvinas)": "FLK",
        "Faroe Islands": "FRO",
        "Fiji": "FJI",
        "Finland": "FIN",
        "France": "FRA",
        "French Guiana": "GUF",
        "French Polynesia": "PYF",
        "French Southern Territories": "ATF",
        "Gabon": "GAB",
        "Gambia": "GMB",
        "Georgia": "GEO",
        "Germany": "DEU",
        "Ghana": "GHA",
        "Gibraltar": "GIB",
        "Greece": "GRC",
        "Greenland": "GRL",
        "Grenada": "GRD",
        "Guadeloupe": "GLP",
        "Guam": "GUM",
        "Guatemala": "GTM",
        "Guernsey": "GGY",
        "Guinea": "GIN",
        "Guinea-Bissau": "GNB",
        "Guyana": "GUY",
        "Haiti": "HTI",
        "Heard Island and McDonald Islands": "HMD",
        "Holy See (Vatican City State)": "VAT",
        "Honduras": "HND",
        "Hong Kong": "HKG",
        "Hungary": "HUN",
        "Iceland": "ISL",
        "India": "IND",
        "Indonesia": "IDN",
        "Iran, Islamic Republic of": "IRN",
        "Iran": "IRN",
        "Iraq": "IRQ",
        "Ireland": "IRL",
        "Isle of Man": "IMN",
        "Israel": "ISR",
        "Italy": "ITA",
        "Jamaica": "JAM",
        "Japan": "JPN",
        "Jersey": "JEY",
        "Jordan": "JOR",
        "Kazakhstan": "KAZ",
        "Kenya": "KEN",
        "Kiribati": "KIR",
        "Korea, Democratic People's Republic of": "PRK",
        "Korea, Republic of": "KOR",
        "Kuwait": "KWT",
        "Kyrgyzstan": "KGZ",
        "Lao People's Democratic Republic": "LAO",
        "Latvia": "LVA",
        "Lebanon": "LBN",
        "Lesotho": "LSO",
        "Liberia": "LBR",
        "Libya": "LBY",
        "Liechtenstein": "LIE",
        "Lithuania": "LTU",
        "Luxembourg": "LUX",
        "Macao": "MAC",
        "Macedonia, the Former Yugoslav Republic of": "MKD",
        "Macedonia": "MKD",
        "Madagascar": "MDG",
        "Malawi": "MWI",
        "Malaysia": "MYS",
        "Maldives": "MDV",
        "Mali": "MLI",
        "Malta": "MLT",
        "Marshall Islands": "MHL",
        "Martinique": "MTQ",
        "Mauritania": "MRT",
        "Mauritius": "MUS",
        "Mayotte": "MYT",
        "Mexico": "MEX",
        "Micronesia, Federated States of": "FSM",
        "Moldova, Republic of": "MDA",
        "Moldova": "MDA",
        "Monaco": "MCO",
        "Mongolia": "MNG",
        "Montenegro": "MNE",
        "Montserrat": "MSR",
        "Morocco": "MAR",
        "Mozambique": "MOZ",
        "Myanmar": "MMR",
        "Namibia": "NAM",
        "Nauru": "NRU",
        "Nepal": "NPL",
        "Netherlands": "NLD",
        "New Caledonia": "NCL",
        "New Zealand": "NZL",
        "Nicaragua": "NIC",
        "Niger": "NER",
        "Nigeria": "NGA",
        "Niue": "NIU",
        "Norfolk Island": "NFK",
        "Northern Mariana Islands": "MNP",
        "Norway": "NOR",
        "Oman": "OMN",
        "Pakistan": "PAK",
        "Palau": "PLW",
        "Palestine, State of": "PSE",
        "Panama": "PAN",
        "Papua New Guinea": "PNG",
        "Paraguay": "PRY",
        "Peru": "PER",
        "Philippines": "PHL",
        "Pitcairn": "PCN",
        "Poland": "POL",
        "Portugal": "PRT",
        "Puerto Rico": "PRI",
        "Qatar": "QAT",
        "Romania": "ROU",
        "Russian Federation": "RUS",
        "Rwanda": "RWA",
        "Reunion": "REU",
        "Saint Barthelemy": "BLM",
        "Saint Helena": "SHN",
        "Saint Kitts and Nevis": "KNA",
        "Saint Lucia": "LCA",
        "Saint Martin (French part)": "MAF",
        "Saint Pierre and Miquelon": "SPM",
        "Saint Vincent and the Grenadines": "VCT",
        "Samoa": "WSM",
        "San Marino": "SMR",
        "Sao Tome and Principe": "STP",
        "Saudi Arabia": "SAU",
        "Senegal": "SEN",
        "Serbia": "SRB",
        "Seychelles": "SYC",
        "Sierra Leone": "SLE",
        "Singapore": "SGP",
        "Sint Maarten (Dutch part)": "SXM",
        "Slovakia": "SVK",
        "Slovenia": "SVN",
        "Solomon Islands": "SLB",
        "Somalia": "SOM",
        "South Africa": "ZAF",
        "South Georgia and the South Sandwich Islands": "SGS",
        "South Sudan": "SSD",
        "Spain": "ESP",
        "Sri Lanka": "LKA",
        "Sudan": "SDN",
        "Suriname": "SUR",
        "Svalbard and Jan Mayen": "SJM",
        "Swaziland": "SWZ",
        "Sweden": "SWE",
        "Switzerland": "CHE",
        "Syrian Arab Republic": "SYR",
        "Taiwan": "TWN",
        "Tajikistan": "TJK",
        "United Republic of Tanzania": "TZA",
        "Tanzania": "TZA",
        "Thailand": "THA",
        "Timor-Leste": "TLS",
        "Togo": "TGO",
        "Tokelau": "TKL",
        "Tonga": "TON",
        "Trinidad and Tobago": "TTO",
        "Tunisia": "TUN",
        "Turkey": "TUR",
        "Turkmenistan": "TKM",
        "Turks and Caicos Islands": "TCA",
        "Tuvalu": "TUV",
        "Uganda": "UGA",
        "Ukraine": "UKR",
        "United Arab Emirates": "ARE",
        "United Kingdom": "GBR",
        "United States": "USA",
        "United States Minor Outlying Islands": "UMI",
        "Uruguay": "URY",
        "Uzbekistan": "UZB",
        "Vanuatu": "VUT",
        "Venezuela": "VEN",
        "Viet Nam": "VNM",
        "British Virgin Islands": "VGB",
        "US Virgin Islands": "VIR",
        "Wallis and Futuna": "WLF",
        "Western Sahara": "ESH",
        "Yemen": "YEM",
        "Zambia": "ZMB",
        "Zimbabwe": "ZWE",
        "USA": "USA",
        "Russia": "RUS",
        "Atlantic Ocean": "ATL",
        "Pacific Ocean": "PAC",
        "None": "UNK",
        "UNK": "None",
        "Kosova": 'KOS',
        "Arctic Ocean": 'ARO'
        }

    if inverted:
        return dict([[v, k] for k, v in d.items()])

    return d


def get_country_from_geo_loc(geographic_location):
    '''
    Parser to get country from standard NCBI geographic_location fields
    '''

    countries = get_country_codes(inverted=False)
    loc = 'UNK'

    if geographic_location in countries:
        loc = countries[geographic_location]

    else:
        if ':' in geographic_location:
            country = geographic_location.split(':')[0]
            print('COUNTRY = ',  country)
            if country.title() in countries:
                loc = countries[country.title()]
            elif country in countries:
                loc = countries[country]

        else:
            for word in geographic_location.split(' '):
                word = re.sub('[^A-Za-z]', '', word)
                print('Word = ', word)
                if word.title() in countries:
                    loc = countries[word.title()]
                    print(loc)
                    break
                elif word in countries:
                    loc = countries[word]
                    print(loc)
                    break
    if loc == 'UNK':
        raise ValueError(f'Cannot find a country in {geographic_location}. Message audra')

    return loc
