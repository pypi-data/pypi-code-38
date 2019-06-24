# -*- coding: utf-8 -*-
'''
Deze module mapt binnenkomende json objecten naar database objecten.
'''
from ..data.models import (
    Perceel,
    LocatieElement,
    LocatieAdres,
    OpenbaarDomein,
)
from ..utils import convert_geojson_to_wktelement


def _map_locatie(locatie_json, resource):
    '''
    Mapt een locatie_json in json formaat tot de benodigde velden in een resource object
    :param locatie_json: Een dict die de JSON voorstelt die naar onze service
            gezonden werd.
    :param resource: resource object
    :returns: resource object
    '''
    resource.contour = convert_geojson_to_wktelement(locatie_json.get('contour'))
    resource.locatie_elementen = _map_locatie_elementen(locatie_json.get('elementen', []))
    return resource


def _map_locatie_elementen(locatie_elementen_json):
    '''
    Mapt een locatie_elementen_json in json formaat tot een :class:`oe_geoutils.data.models.LocatieElement`
    of 1 van de children van deze class
    :param locatie_elementen_json: Een dict die de JSON voorstelt die naar onze service gezonden werd.
    :rtype: list of :class:`oe_geoutils.data.models.LocatieElement`
    '''
    locatie_elementen = []
    for locatie_element in locatie_elementen_json:
        if locatie_element.get('type') == 'https://id.erfgoed.net/vocab/ontology#LocatieElement':
            locatie_elementen.append(
                LocatieElement(
                    type='https://id.erfgoed.net/vocab/ontology#LocatieElement',
                    provincie_niscode=locatie_element.get('provincie').get('niscode'),
                    provincie_naam=locatie_element.get('provincie').get('naam'),
                    gemeente_niscode=locatie_element.get('gemeente').get('niscode'),
                    gemeente_naam=locatie_element.get('gemeente').get('naam'),
                    deelgemeente_niscode=locatie_element.get('deelgemeente', {}).get('niscode'),
                    deelgemeente_naam=locatie_element.get('deelgemeente', {}).get('naam'),
                    gemeente_crab_id=locatie_element.get('gemeente').get('id')
                )
            )
        if locatie_element.get('type') == 'https://id.erfgoed.net/vocab/ontology#LocatieElementPerceel':
            locatie_elementen.append(
                Perceel(
                    type='https://id.erfgoed.net/vocab/ontology#LocatieElementPerceel',
                    provincie_niscode=locatie_element.get('provincie').get('niscode'),
                    provincie_naam=locatie_element.get('provincie').get('naam'),
                    gemeente_niscode=locatie_element.get('gemeente').get('niscode'),
                    gemeente_naam=locatie_element.get('gemeente').get('naam'),
                    deelgemeente_niscode=locatie_element.get('deelgemeente', {}).get('niscode'),
                    deelgemeente_naam=locatie_element.get('deelgemeente', {}).get('naam'),
                    gemeente_crab_id=locatie_element.get('gemeente').get('id'),
                    afdeling=locatie_element.get('perceel').get('afdeling'),
                    sectie=locatie_element.get('perceel').get('sectie'),
                    perceel=locatie_element.get('perceel').get('perceel'),
                    capakey=locatie_element.get('perceel').get('capakey')
                )
            )
        if locatie_element.get('type') == 'https://id.erfgoed.net/vocab/ontology#LocatieElementOpenbaarDomein':
            locatie_elementen.append(
                OpenbaarDomein(
                    type='https://id.erfgoed.net/vocab/ontology#LocatieElementOpenbaarDomein',
                    provincie_niscode=locatie_element.get('provincie').get('niscode'),
                    provincie_naam=locatie_element.get('provincie').get('naam'),
                    gemeente_niscode=locatie_element.get('gemeente').get('niscode'),
                    gemeente_naam=locatie_element.get('gemeente').get('naam'),
                    deelgemeente_niscode=locatie_element.get('deelgemeente', {}).get('niscode'),
                    deelgemeente_naam=locatie_element.get('deelgemeente', {}).get('naam'),
                    gemeente_crab_id=locatie_element.get('gemeente').get('id'),
                    omschrijving=locatie_element.get('omschrijving')
                )
            )
        if locatie_element.get('type') == 'https://id.erfgoed.net/vocab/ontology#LocatieElementAdres':
            locatie_elementen.append(
                LocatieAdres(
                    type='https://id.erfgoed.net/vocab/ontology#LocatieElementAdres',
                    provincie_niscode=locatie_element.get('provincie').get('niscode'),
                    provincie_naam=locatie_element.get('provincie').get('naam'),
                    gemeente_niscode=locatie_element.get('gemeente').get('niscode'),
                    deelgemeente_niscode=locatie_element.get('deelgemeente', {}).get('niscode'),
                    deelgemeente_naam=locatie_element.get('deelgemeente', {}).get('naam'),
                    gemeente_naam=locatie_element.get('gemeente').get('naam'),
                    gemeente_crab_id=locatie_element.get('gemeente').get('id'),
                    straat_id=locatie_element.get('straat_id'),
                    straat=locatie_element.get('straat'),
                    huisnummer_id=locatie_element.get('huisnummer_id'),
                    huisnummer=locatie_element.get('huisnummer'),
                    subadres_id=locatie_element.get('subadres_id'),
                    subadres=locatie_element.get('subadres'),
                    postcode=locatie_element.get('postcode'),
                    land=locatie_element.get('land')
                )
            )
    return locatie_elementen
