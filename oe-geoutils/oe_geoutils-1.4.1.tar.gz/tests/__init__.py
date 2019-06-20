# -*- coding: utf-8 -*-
import json
import os
import re
import sys

import responses
from crabpy.gateway.exception import GatewayRuntimeException

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock  # pragma: no cover

from oe_geoutils.data.models import (
    LocatieElement,
    LocatieAdres,
    Perceel,
    OpenbaarDomein,
)

# gewest en provincies

gewest_mock = Mock()

antwerpen = Mock()
antwerpen.naam = "Antwerpen"
antwerpen.gewest = gewest_mock
antwerpen.niscode = 10000

vlbranbant = Mock()
vlbranbant.naam = "Vlaams-Brabant"
vlbranbant.gewest = gewest_mock
vlbranbant.niscode = 20001

wvlaanderen = Mock()
wvlaanderen.naam = "West-Vlaanderen"
wvlaanderen.gewest = gewest_mock
wvlaanderen.niscode = 30000

ovlaanderen = Mock()
ovlaanderen.naam = "Oost-Vlaanderen"
ovlaanderen.gewest = gewest_mock
ovlaanderen.niscode = 40000

limburg = Mock()
limburg.naam = "Limburg"
limburg.gewest = gewest_mock
limburg.niscode = 70000

# Knokke-Heist

pk_8300_mock = Mock()
pk_8300_mock.id = 8300

pk_3000_mock = Mock()
pk_3000_mock.id = 3000

pk_8301_mock = Mock()
pk_8301_mock.id = 8301

pk_2610_mock = Mock()
pk_2610_mock.id = 2610

pk_2180_mock = Mock()
pk_2180_mock.id = 2180

ns_num_6_sub_mock = Mock()
ns_num_6_sub_mock.id = 1441952
ns_num_6_sub_mock.huisnummer_id = 270059
ns_num_6_sub_mock.subadres = "1"

ns_num_69_sub_mock = Mock()
ns_num_69_sub_mock.id = 1442188
ns_num_69_sub_mock.huisnummer_id = 882821
ns_num_69_sub_mock.subadres = "11"

ns_num_6_mock = Mock()
ns_num_6_mock.id = 270059
ns_num_6_mock.straat_id = 48086
ns_num_6_mock.huisnummer = "6"
ns_num_6_mock.subadressen = [ns_num_6_sub_mock]
ns_num_6_mock.postkanton = pk_8300_mock

ns_num_40_2180_mock = Mock()
ns_num_40_2180_mock.id = 2292449
ns_num_40_2180_mock.straat_id = 356
ns_num_40_2180_mock.huisnummer = "40"
ns_num_40_2180_mock.subadressen = []
ns_num_40_2180_mock.postkanton = pk_2180_mock

ns_num_40_2610_mock = Mock()
ns_num_40_2610_mock.id = 4228194
ns_num_40_2610_mock.straat_id = 355
ns_num_40_2610_mock.huisnummer = "40"
ns_num_40_2610_mock.subadressen = []
ns_num_40_2610_mock.postkanton = pk_2610_mock

ns_num_75_34819_mock = Mock()
ns_num_75_34819_mock.id = 201984
ns_num_75_34819_mock.straat_id = 34819
ns_num_75_34819_mock.huisnummer = "75"
ns_num_75_34819_mock.postkanton = pk_3000_mock

ns_num_68_mock = Mock()
ns_num_68_mock.id = 887821
ns_num_68_mock.straat_id = 48086
ns_num_68_mock.huisnummer = "68"
ns_num_68_mock.subadressen = [ns_num_69_sub_mock]
ns_num_68_mock.postkanton = pk_8300_mock

ns_num_69_mock = Mock()
ns_num_69_mock.id = 882821
ns_num_69_mock.straat_id = 43086
ns_num_69_mock.huisnummer = "69"
ns_num_69_mock.subadressen = []
ns_num_69_mock.postkanton = pk_8300_mock

nieuwstraat_mock = Mock()
nieuwstraat_mock.id = 48086
nieuwstraat_mock.gemeente_id = 191
nieuwstraat_mock.label = "Nieuwstraat"
nieuwstraat_mock.huisnummers = [ns_num_6_mock, ns_num_68_mock]

bist_2180_mock = Mock()
bist_2180_mock.id = 356
bist_2180_mock.gemeente_id = 2
bist_2180_mock.label = "Bist"
bist_2180_mock.huisnummers = [ns_num_40_2180_mock]

bist_2610_mock = Mock()
bist_2610_mock.id = 355
bist_2610_mock.gemeente_id = 2
bist_2610_mock.label = "Bist"
bist_2610_mock.huisnummers = [ns_num_40_2610_mock]

fontein_mock = Mock()
fontein_mock.id = 34819
fontein_mock.label = "Fonteinstraat"
fontein_mock.gemeente_id = 143
fontein_mock.huisnummers = [ns_num_75_34819_mock]

knokke_mock = Mock()
knokke_mock.id = 191
knokke_mock.naam = "Knokke-Heist"
knokke_mock.niscode = 31043
knokke_mock.provincie = wvlaanderen
knokke_mock.straten = [nieuwstraat_mock]
knokke_mock.postkantons = [pk_8300_mock, pk_8301_mock]

# Lier

pk_2500_mock = Mock()
pk_2500_mock.id = 2500

lier_mock = Mock()
lier_mock.id = 36
lier_mock.naam = "Lier"
lier_mock.niscode = 12021
lier_mock.provincie = antwerpen
lier_mock.straten = []
lier_mock.postkantons = [pk_2500_mock]

# Leuven

leuven_mock = Mock()
leuven_mock.id = 143
leuven_mock.naam = "Leuven"
leuven_mock.niscode = 24062
leuven_mock.provincie = vlbranbant
leuven_mock.straten = [fontein_mock]
leuven_mock.postkantons = []

# Antwerpen

antwerpen_mock = Mock()
antwerpen_mock.id = 2
antwerpen_mock.naam = "Antwerpen"
antwerpen_mock.niscode = 11002
antwerpen_mock.provincie = antwerpen
antwerpen_mock.straten = [bist_2610_mock, bist_2180_mock]
antwerpen_mock.postkantons = []

gewest_mock.gemeentes = [knokke_mock, lier_mock, leuven_mock, antwerpen_mock]

# ---------------

gewest_mock_dict = {1: gewest_mock, 2: gewest_mock, 3: gewest_mock}
gemeente_mock_dict = {191: knokke_mock, 36: lier_mock, 143: leuven_mock, 2: antwerpen_mock}
gemeente_niscode_mock_dict = {31043: knokke_mock, 12021: lier_mock, 24062: leuven_mock, 11002: antwerpen_mock}
deelgemeente_parent_niscode_mock_dict = {24062: [
    Mock(naam='Heverlee', gemeente_niscode=24062, id=None),
    Mock(naam='Kessel - Lo', gemeente_niscode=24062, id='24061X'),
    Mock(naam='Wilsele', gemeente_niscode=24062, id='24062X')]}
straten_mock_dict = {48086: nieuwstraat_mock, 355: bist_2610_mock, 356: bist_2180_mock, 34819: fontein_mock}
num_mock_dict = {270059: ns_num_6_mock, 882821: ns_num_69_mock, 887821: ns_num_68_mock, 2292449: ns_num_40_2180_mock,
                 4228194: ns_num_40_2610_mock, 201984: ns_num_75_34819_mock}
subadres_mock_dict = {1441952: ns_num_6_sub_mock, 1442188: ns_num_69_sub_mock}


def list_gemeenten(gewest_id):
    if gewest_id in gewest_mock_dict:
        return gewest_mock_dict[gewest_id].gemeentes
    else:
        return None


def get_gemeente_by_id(id):
    if id in gemeente_mock_dict:
        return gemeente_mock_dict[id]
    else:
        raise GatewayRuntimeException("ongeldige gemeente", Mock())


def get_gemeente_by_niscode(niscode):
    if niscode in gemeente_niscode_mock_dict:
        return gemeente_niscode_mock_dict[niscode]
    else:
        raise GatewayRuntimeException("ongeldige gemeente", Mock())


def list_deelgemeenten_by_gemeente(gemeente):
    return deelgemeente_parent_niscode_mock_dict[gemeente.niscode]


def deelgemeenten_list():
    return {"24062X": {'naam': 'Wilsele', 'gemeente_niscode': 24062, 'id': '24062X'}}


def get_straat_by_id(id):
    if id in straten_mock_dict:
        return straten_mock_dict[id]
    else:
        raise GatewayRuntimeException("ongeldige straat", Mock())


def get_huisnummer_by_id(id):
    if id in num_mock_dict:
        return num_mock_dict[id]
    else:
        raise GatewayRuntimeException("ongeldig huisnummer", Mock())


def get_subadres_by_id(id):
    if id in subadres_mock_dict:
        return subadres_mock_dict[id]
    else:
        raise GatewayRuntimeException("ongeldig subadres", Mock())


def get_postkanton_by_huisnummer(hn_id):
    if hn_id in num_mock_dict:
        return num_mock_dict[hn_id].postkanton
    else:
        return None


def list_postkantons_by_gemeente(gem_id):
    if gem_id in gemeente_mock_dict:
        return gemeente_mock_dict[gem_id].postkantons
    else:
        return None


def list_provincies(gew_id):
    if gew_id == 2:
        return [antwerpen, vlbranbant, wvlaanderen, ovlaanderen, limburg]
    else:
        return []


crab_gateway_mock = Mock(deelgemeenten=deelgemeenten_list())
crab_gateway_mock.get_gemeente_by_id = get_gemeente_by_id
crab_gateway_mock.get_straat_by_id = get_straat_by_id
crab_gateway_mock.get_huisnummer_by_id = get_huisnummer_by_id
crab_gateway_mock.get_subadres_by_id = get_subadres_by_id
crab_gateway_mock.get_postkanton_by_huisnummer = get_postkanton_by_huisnummer
crab_gateway_mock.list_postkantons_by_gemeente = list_postkantons_by_gemeente
crab_gateway_mock.list_gemeenten = list_gemeenten
crab_gateway_mock.list_provincies = list_provincies
crab_gateway_mock.get_gemeente_by_niscode = get_gemeente_by_niscode
crab_gateway_mock.list_deelgemeenten_by_gemeente = list_deelgemeenten_by_gemeente
afdeling1 = Mock()
afdeling1.id = 66666
afdeling1.naam = "test "
afdeling1.gemeente.id = 12004

afdeling2 = Mock()
afdeling2.id = 24505
afdeling2.naam = "LEUVEN  5 AFD"
afdeling2.gemeente.id = 24062

afdeling3 = Mock()
afdeling3.id = 123456
afdeling3.naam = "test x"
afdeling3.gemeente.id = 31043


def list_kadastrale_afdelingen():
    return [afdeling1, afdeling2, afdeling3]


capakey_gateway_mock = Mock()
capakey_gateway_mock.list_kadastrale_afdelingen = list_kadastrale_afdelingen


def text_(s, encoding='latin-1', errors='strict'):
    """ If ``s`` is an instance of ``binary_type``, return
    ``s.decode(encoding, errors)``, otherwise return ``s``"""
    # True if we are running on Python 3.
    PY3 = sys.version_info[0] == 3
    if PY3:
        binary_type = bytes
    else:
        binary_type = str
    if isinstance(s, binary_type):
        return s.decode(encoding, errors)
    return s


with open(os.path.join(os.path.dirname(__file__), 'fixtures/get_gemeente_results.json'), 'rb') as f:
    get_gemeente_results = json.loads(text_(f.read()))
with open(os.path.join(os.path.dirname(__file__), 'fixtures/get_provincie_results.json'), 'rb') as f:
    get_provincie_results = json.loads(text_(f.read()))


def mock_geozoekdiensten_response(base_url='http://geozoekdienst.en', response_status=200):
    def callback(request):
        resp_body = [{'naam': 'gemeente'}]
        headers = {'content_type': 'application/json'}
        return response_status, headers, json.dumps(resp_body)

    responses.add_callback(
        responses.POST,
        re.compile(r'^({0}).+'.format(base_url)),
        callback=callback)
    return base_url


def mock_geozoekdiensten_get_gemeente_response(len_results, base_url='http://geozoekdienst.en'):
    def callback(request):
        if len_results == 2:
            resp_body = get_gemeente_results
        elif len_results == 1:
            resp_body = [{'naam': 'gemeente', 'id': 'niscode'}]
        else:
            resp_body = []
        headers = {'content_type': 'application/json'}
        return 200, headers, json.dumps(resp_body)

    responses.add_callback(
        responses.POST,
        re.compile(r'^({0}).+'.format(base_url)),
        callback=callback)
    return base_url


def get_Perceel_object():
    return Perceel(
        id=1,
        type='https://id.erfgoed.net/vocab/ontology#LocatieElementPerceel',
        resource_object_id=9999,
        provincie_niscode=20001,
        provincie_naam='Vlaams-Brabant',
        gemeente_niscode=24062,
        gemeente_naam='Leuven',
        gemeente_crab_id=143,
        afdeling='LEUVEN  5 AFD',
        sectie='F',
        perceel='0415/00F000',
        capakey='24505F0415/00F000',
        deelgemeente_niscode='24086X',
        deelgemeente_naam='Oud-Heverlee'
    )


def get_LocatieAdres_object():
    return LocatieAdres(
        id=2,
        type='https://id.erfgoed.net/vocab/ontology#LocatieElementAdres',
        resource_object_id=9999,
        provincie_niscode=20001,
        provincie_naam='Vlaams-Brabant',
        gemeente_niscode=24062,
        gemeente_naam='Leuven',
        gemeente_crab_id=143,
        straat_id=34819,
        straat='Fonteinstraat',
        huisnummer_id=201984,
        huisnummer='75',
        subadres_id=2,
        subadres='test2',
        postcode='3000',
        land='BE',
        deelgemeente_niscode='24086X',
        deelgemeente_naam='Oud-Heverlee'
    )


def get_OpenbaarDomein_object():
    return OpenbaarDomein(
        id=3,
        type='https://id.erfgoed.net/vocab/ontology#LocatieElementOpenbaarDomein',
        resource_object_id=9999,
        provincie_niscode=20001,
        provincie_naam='Vlaams-Brabant',
        gemeente_niscode=24062,
        gemeente_naam='Leuven',
        gemeente_crab_id=143,
        omschrijving='Universiteitsbibliotheek Leuven',
        deelgemeente_niscode='24086X',
        deelgemeente_naam='Oud-Heverlee'
    )


def get_LocatieElement_object():
    return LocatieElement(
        id=4,
        type='https://id.erfgoed.net/vocab/ontology#LocatieElement',
        resource_object_id=9999,
        provincie_niscode=20001,
        provincie_naam='Vlaams-Brabant',
        gemeente_niscode=24062,
        gemeente_naam='Leuven',
        gemeente_crab_id=143,
        deelgemeente_niscode='24086X',
        deelgemeente_naam='Oud-Heverlee'
    )
