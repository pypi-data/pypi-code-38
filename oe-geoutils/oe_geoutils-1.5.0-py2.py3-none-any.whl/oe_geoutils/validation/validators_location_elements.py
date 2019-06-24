# -*- coding: utf-8 -*-
"""
This module validates an location elements.
For an address in Belgium the validation uses the CRAB principles.
"""
import logging

import re
import colander
import pycountry
from colander import null
from crabpy.gateway.exception import GatewayRuntimeException, GatewayResourceNotFoundException
from oe_geoutils.validation.validators_address import process_huisnummer, process_subadres, process_straat
from oe_geoutils.validation.validators_cadaster_parcels import CadasterSchemaNode
import copy

log = logging.getLogger(__name__)


class ProvincieSchemaNode(colander.MappingSchema):
    naam = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(1, 50),
        missing=None
    )
    niscode = colander.SchemaNode(
        colander.Integer(),
        missing=None
    )


class GemeenteSchemaNode(colander.MappingSchema):
    naam = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(1, 255),
        missing=None
    )
    id = colander.SchemaNode(
        colander.Integer(),
        missing=None
    )
    niscode = colander.SchemaNode(
        colander.Integer(),
        missing=None
    )


class DeelGemeenteSchemaNode(colander.MappingSchema):
    naam = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(1, 255),
        missing=None
    )

    niscode = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(1, 10),
        missing=None
    )


def _get_hoofd_niscode(deelgemeente_niscode):
    """
    :param string niscode van deelgemeente e.g.("24062A")
    :return: int niscode fusiegemeente e.g.(24062)
    """
    if re.match('^[0-9]{5}[a-zA-Z]{1,1}$', deelgemeente_niscode):
        return int(deelgemeente_niscode[:-1])
    elif re.match('^[0-9]{5}', deelgemeente_niscode):
        return int(deelgemeente_niscode)
    else:
        raise Exception('invalid deelgemeente niscode')


class LocationElementSchemaNode(colander.MappingSchema):
    id = colander.SchemaNode(
        colander.Integer(),
        missing=None
    )

    type = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(1, 250)
    )

    provincie = ProvincieSchemaNode(
        missing={}
    )

    gemeente = GemeenteSchemaNode(
        missing={}
    )

    deelgemeente = DeelGemeenteSchemaNode(
        missing={}
    )

    straat = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(1, 100),
        missing=None
    )

    straat_id = colander.SchemaNode(
        colander.Integer(),
        missing=None
    )

    huisnummer = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(1, 40),
        missing=None
    )

    huisnummer_id = colander.SchemaNode(
        colander.Integer(),
        missing=None
    )

    subadres = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(1, 20),
        missing=None
    )

    subadres_id = colander.SchemaNode(
        colander.Integer(),
        missing=None
    )

    postcode = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(1, 20),
        missing=None
    )

    land = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(1, 100),
        missing='BE'
    )

    perceel = CadasterSchemaNode(
        missing=None
    )

    omschrijving = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(1, 250),
        missing=None
    )

    def preparer(self, input_locatie_element):
        locatie_element = copy.deepcopy(input_locatie_element)
        if locatie_element is None or not locatie_element:
            return null  # pragma: no cover
        request = self.bindings['request']
        crab_gateway = request.crab_gateway()
        capakey_gateway = request.capakey_gateway()
        locatie_element_type = ''
        if 'type' in locatie_element:
            locatie_element_type = locatie_element.get('type')
        if 'land' in locatie_element and locatie_element.get('land').upper() == 'BE':
            if locatie_element_type == 'https://id.erfgoed.net/vocab/ontology#LocatieElementAdres':
                locatie_element = self._prepare_locatie_adres(crab_gateway, locatie_element)
            elif locatie_element_type == 'https://id.erfgoed.net/vocab/ontology#LocatieElementPerceel':
                locatie_element = self._prepare_locatie_perceel(capakey_gateway, crab_gateway, locatie_element)
            elif locatie_element_type == 'https://id.erfgoed.net/vocab/ontology#LocatieElementOpenbaarDomein':
                locatie_element = self._prepare_locatie(crab_gateway, locatie_element)
            elif locatie_element_type == 'https://id.erfgoed.net/vocab/ontology#LocatieElement':
                locatie_element = self._prepare_locatie(crab_gateway, locatie_element)
        else:
            locatie_element['gemeente']['id'] = None
            locatie_element['straat_id'] = None
            locatie_element['huisnummer_id'] = None
            locatie_element['subadres_id'] = None
        if 'land' in locatie_element:
            locatie_element['land'] = locatie_element.get('land').upper()
        return locatie_element

    def validator(self, node, locatie_element):
        request = self.bindings['request']
        crab_gateway = request.crab_gateway()
        capakey_gateway = request.capakey_gateway()
        locatie_element_type = ''
        land = None
        if 'type' in locatie_element:
            locatie_element_type = locatie_element.get('type')
        if 'land' in locatie_element:
            land = locatie_element.get('land')
            try:
                try:
                    pycountry.countries.get(alpha2=land)
                except KeyError:
                    pycountry.countries.get(alpha_2=land)
            except KeyError:
                raise colander.Invalid(
                    node,
                    'ongeldige landcode %s, dit is geen ISO 3166 code' %
                    land
                )
        if land == 'BE':
            if locatie_element_type == 'https://id.erfgoed.net/vocab/ontology#LocatieElementAdres':
                self._validate_locatie_adres(crab_gateway, locatie_element, node)
            if locatie_element_type == 'https://id.erfgoed.net/vocab/ontology#LocatieElementPerceel':
                self._validate_locatie_perceel(capakey_gateway, locatie_element, node)
            if locatie_element_type == 'https://id.erfgoed.net/vocab/ontology#LocatieElementOpenbaarDomein':
                self._validate_locatie_openbaar_domein(locatie_element, node)
            if locatie_element_type == 'https://id.erfgoed.net/vocab/ontology#LocatieElement':
                self._validate_locatie(locatie_element, node)

    @staticmethod
    def _prepare_locatie_adres(crab_gateway, locatie_element):
        # Gemeente
        if locatie_element.get('gemeente', {}).get('id', None) is None:
            if locatie_element.get('gemeente', {}).get('naam', None) is None:
                return locatie_element

            gemeente = locatie_element.get('gemeente', {}).get('naam')
            gewest_ids = [2, 1, 3]
            for gewest_id in gewest_ids:
                gemeenten = crab_gateway.list_gemeenten(gewest_id)
                gemeente_val = next((g for g in gemeenten if g.naam.lower() == gemeente.lower()), None)
                if gemeente_val:
                    locatie_element['gemeente']['id'] = gemeente_val.id
                    break
            if locatie_element.get('gemeente', {}).get('id', None) is None:
                return locatie_element

        # gemeente id gekend
        gemeente_id = locatie_element.get('gemeente', {}).get('id', None)
        straat_id = locatie_element.get('straat_id', None)
        straat = locatie_element.get('straat', None)
        huisnummer_id = locatie_element.get('huisnummer_id', None)
        huisnummer = locatie_element.get('huisnummer', None)
        subadres_id = locatie_element.get('subadres_id', None)
        subadres = locatie_element.get('subadres', None)
        try:
            gemeente = crab_gateway.get_gemeente_by_id(gemeente_id)
        except (GatewayRuntimeException, AttributeError):
            locatie_element['gemeente']['naam'] = None
            return locatie_element

        if gemeente:
            locatie_element['gemeente']['naam'] = "" + gemeente.naam
            locatie_element['gemeente']['niscode'] = gemeente.niscode
            locatie_element['provincie']['niscode'] = gemeente.provincie.niscode
            locatie_element['provincie']['naam'] = gemeente.provincie.naam
            if straat_id:
                straat_val = next((s for s in gemeente.straten if s.id == straat_id), None)
                if straat_val:
                    locatie_element['straat'] = "" + straat_val.label
                    num_val = process_huisnummer(locatie_element, huisnummer_id, huisnummer, straat_val)
                    if num_val:
                        process_subadres(locatie_element, subadres_id, subadres, num_val)
            if not straat_id and straat:
                straat_val = process_straat(locatie_element, straat, gemeente, crab_gateway)
                if straat_val:
                    locatie_element['straat_id'] = straat_val.id
                    num_val = process_huisnummer(locatie_element, huisnummer_id, huisnummer, straat_val)
                    if num_val:
                        process_subadres(locatie_element, subadres_id, subadres, num_val)
        _set_deelgemeente(locatie_element, gemeente, crab_gateway)
        return locatie_element

    @staticmethod
    def _prepare_locatie_perceel(capakey_gateway, crab_gateway, locatie_element):
        try:
            kadastrale_afdelingen = capakey_gateway.list_kadastrale_afdelingen()
            capakey = locatie_element['perceel']['capakey']
            afdeling_niscode = int(capakey[0:5])
            afdeling = next((afd for afd in kadastrale_afdelingen if afd.id == afdeling_niscode), None)
            if afdeling:
                locatie_element['perceel']['sectie'] = capakey[5:6]
                locatie_element['perceel']['perceel'] = capakey[6:]
                locatie_element['perceel']['afdeling'] = afdeling.naam
                gemeente = crab_gateway.get_gemeente_by_niscode(afdeling.gemeente.id)
                locatie_element['gemeente']['id'] = gemeente.id
                locatie_element['gemeente']['naam'] = gemeente.naam
                locatie_element['gemeente']['niscode'] = afdeling.gemeente.id
                _set_deelgemeente(locatie_element, gemeente, crab_gateway)
                locatie_element['provincie']['niscode'] = gemeente.provincie.niscode
                locatie_element['provincie']['naam'] = gemeente.provincie.naam
        except (GatewayRuntimeException, AttributeError, GatewayResourceNotFoundException) as e:
            log.warning("Failed to prepare the locatie perceel. Skipping...")
        return locatie_element

    @staticmethod
    def _prepare_locatie(crab_gateway, locatie_element):
        gemeente = None
        gemeente_id = locatie_element.get('gemeente', {}).get('id', None)
        gemeente_niscode = locatie_element.get('gemeente', {}).get('niscode', None)
        gemeente_naam = locatie_element.get('gemeente', {}).get('naam', None)
        if gemeente_id:
            try:
                gemeente = crab_gateway.get_gemeente_by_id(gemeente_id)
            except (GatewayRuntimeException, AttributeError):
                gemeente = None
        if gemeente is None and gemeente_niscode:
            try:
                gemeente = crab_gateway.get_gemeente_by_niscode(gemeente_niscode)
            except (GatewayRuntimeException, AttributeError):
                gemeente = None
        if gemeente is None and gemeente_naam:
            gewest_ids = [2, 1, 3]
            for gewest_id in gewest_ids:
                try:
                    gemeenten = crab_gateway.list_gemeenten(gewest_id)
                    gemeente = next((g for g in gemeenten if g.naam.lower() == gemeente_naam.lower()), None)
                    if gemeente:
                        break
                except (GatewayRuntimeException, AttributeError):  # pragma no cover
                    gemeente = None
        if gemeente:
            locatie_element['gemeente']['id'] = gemeente.id
            locatie_element['gemeente']['naam'] = gemeente.naam
            locatie_element['gemeente']['niscode'] = gemeente.niscode
            locatie_element['provincie']['niscode'] = gemeente.provincie.niscode
            locatie_element['provincie']['naam'] = gemeente.provincie.naam
            _set_deelgemeente(locatie_element, gemeente, crab_gateway)
        else:
            locatie_element['gemeente']['id'] = None
        return locatie_element

    @staticmethod
    def _validate_provincie_gemeente(locatie_element, node):
        gemeente = locatie_element.get('gemeente', {}).get('naam', None)
        gemeente_id = locatie_element.get('gemeente', {}).get('id', None)
        gemeente_niscode = locatie_element.get('gemeente', {}).get('niscode', None)
        provincie = locatie_element.get('provincie', {}).get('naam', None)
        provincie_niscode = locatie_element.get('provincie', {}).get('niscode', None)
        if gemeente_id is None:
            raise colander.Invalid(
                node,
                'geen correcte gemeente_id gevonden voor de gemeente {0}'.format(gemeente)
            )
        if gemeente is None:  # if gemeente is still None here, the gemeente_id was incorrect
            raise colander.Invalid(
                node,
                'ongeldig gemeente_id {0}'.format(gemeente_id)
            )
        if gemeente_niscode is None:  # pragma no cover  # normally the first 2 checks will fail in this case
            raise colander.Invalid(
                node,
                'ongeldige gemeente_niscode {0}'.format(gemeente_niscode)
            )
        if provincie is None:  # pragma no cover   # normally the first 2 checks will fail in this case
            raise colander.Invalid(
                node,
                'ongeldige provincie {0}'.format(provincie)
            )
        if provincie_niscode is None:  # pragma no cover   # normally the first 2 checks will fail in this case
            raise colander.Invalid(
                node,
                'ongeldige provincie_niscode {0}'.format(provincie_niscode)
            )

    def _validate_locatie_perceel(self, capakey_gateway, locatie_element, node):
        self._validate_provincie_gemeente(locatie_element, node)
        kadastrale_afdelingen = capakey_gateway.list_kadastrale_afdelingen()
        capakey = locatie_element['perceel']['capakey']
        afdeling_niscode = int(capakey[0:5])
        afdeling = next((afd for afd in kadastrale_afdelingen if afd.id == afdeling_niscode), None)
        if afdeling is None:
            raise colander.Invalid(
                node,
                'ongeldige kadastrale afdeling voor capakey {0}'.format(capakey)
            )

    def _validate_locatie_openbaar_domein(self, locatie_element, node):
        self._validate_provincie_gemeente(locatie_element, node)

    def _validate_locatie(self, locatie_element, node):
        self._validate_provincie_gemeente(locatie_element, node)

    def _validate_locatie_adres(self, crab_gateway, locatie_element, node):
        self._validate_provincie_gemeente(locatie_element, node)
        gemeente_id = locatie_element.get('gemeente', {}).get('id', None)
        straat_id = locatie_element.get('straat_id', None)
        huisnummer_id = locatie_element.get('huisnummer_id', None)
        postcode = locatie_element.get('postcode', None)
        subadres_id = locatie_element.get('subadres_id', None)

        if locatie_element.get('deelgemeente', False):
            # if has deelgemeente naam and no niscode
            if locatie_element.get('deelgemeente').get('naam', False) and \
                    locatie_element.get('deelgemeente').get('niscode', None) is None:
                raise colander.Invalid(node, 'deelgemeente moet een niscode hebben')

        if locatie_element.get('deelgemeente', {}).get('niscode', False) and \
                locatie_element.get('gemeente', {}).get('niscode', False):  # if gemeente and deelgemeente has niscode
            if _get_hoofd_niscode(locatie_element.get('deelgemeente', {}).get('niscode')) != \
                    locatie_element.get('gemeente', {}).get('niscode'):
                raise colander.Invalid(node,
                                       'niscode van gemeente en deelgemeente moet hetzelfde zijn '
                                       '(uitgezonderd, toegevoegde letters van deelgemeentes)')
        if straat_id is not None:
            gemeente = crab_gateway.get_gemeente_by_id(gemeente_id)
            try:
                straat = crab_gateway.get_straat_by_id(straat_id)
            except (GatewayRuntimeException, AttributeError):
                raise colander.Invalid(
                    node,
                    'ongeldig straat_id'
                )
            if straat.gemeente_id != gemeente_id:
                raise colander.Invalid(
                    node,
                    'de straat %s met id %s ligt niet in gemeente %s' %
                    (locatie_element.get('straat', ''), straat_id, gemeente.naam)
                )
            if huisnummer_id is not None:
                try:
                    huisnummer = crab_gateway.get_huisnummer_by_id(huisnummer_id)
                except (GatewayRuntimeException, AttributeError):
                    raise colander.Invalid(
                        node,
                        'ongeldig huisnummer_id'
                    )
                if huisnummer.straat_id != straat_id:
                    raise colander.Invalid(
                        node,
                        'het huisnummer %s met id %s ligt niet in straat %s' %
                        (locatie_element.get('huisnummer', ''), huisnummer_id, straat.label)
                    )
                if postcode is not None:
                    postkanton = crab_gateway.get_postkanton_by_huisnummer(huisnummer_id)
                    if postcode != str(postkanton.id):
                        raise colander.Invalid(
                            node,
                            'postcode %s is niet correct voor dit adres, mogelijke postcode is %s' %
                            (postcode, postkanton.id)
                        )
                if subadres_id is not None:
                    try:
                        subadres = crab_gateway.get_subadres_by_id(subadres_id)
                    except (GatewayRuntimeException, AttributeError):
                        raise colander.Invalid(
                            node,
                            'ongeldig subadres_id'
                        )
                    if subadres.huisnummer_id != huisnummer_id:
                        raise colander.Invalid(
                            node,
                            'het subadres %s met id %s ligt niet op huisnummer %s' %
                            (locatie_element.get('subadres', ''), subadres_id, huisnummer.huisnummer)
                        )
        if straat_id is None and huisnummer_id is not None:
            raise colander.Invalid(
                node,
                'als er een huisnummer_id wordt gegeven, moet men ook het straat_id invullen'
            )
        if huisnummer_id is None and postcode is not None:
            postkantons = crab_gateway.list_postkantons_by_gemeente(gemeente_id)
            postkantons = [str(pk.id) for pk in postkantons]
            if postcode not in postkantons:
                raise colander.Invalid(
                    node,
                    'postcode %s is niet correct voor dit adres, mogelijke postcode(s) zijn %s' %
                    (postcode, postkantons)
                )


def _set_deelgemeente(locatie_element, gemeente, crab_gateway):
    if locatie_element.get('deelgemeente', {}).get('niscode', None) is not None:
        deelgemeente = crab_gateway.deelgemeenten.get(locatie_element.get('deelgemeente', {}).get('niscode'), False)
        if deelgemeente:
            locatie_element['deelgemeente']['naam'] = deelgemeente['naam']

    elif locatie_element.get('deelgemeente', {}).get('naam', None) is not None and gemeente:
        deelgemeentes = crab_gateway.list_deelgemeenten_by_gemeente(gemeente)
        for gem in deelgemeentes:
            if gem.naam == locatie_element.get('deelgemeente', {}).get('naam'):
                locatie_element['deelgemeente']['niscode'] = gem.id
