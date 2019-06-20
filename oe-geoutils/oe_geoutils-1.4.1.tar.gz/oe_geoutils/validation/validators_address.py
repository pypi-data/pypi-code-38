# -*- coding: utf-8 -*-
"""
This module validates an address.
For an address in Belgium the validation uses the CRAB principles.
"""

import colander
from crabpy.gateway.exception import GatewayRuntimeException, GatewayResourceNotFoundException
import pycountry
from colander import null


def process_straat(adres, straat, gemeente, crab_gateway):
    # It is possible to have a street with the same name in one municipality with different postal codes.
    # In this case, if postal code is given, determine the correct street crab id by:
    # - looking up all possible streets with the same name in the given municipality
    # - using the first house number to determine the current postal code and
    # - compare it to the given one.
    postcode = adres.get('postcode')
    if not postcode:
        return next((s for s in gemeente.straten if s.label.lower() == straat.lower()), None)
    else:
        straat_vals = [s for s in gemeente.straten if s.label.lower() == straat.lower()]
        straat_val = straat_vals[0] if straat_vals else None
        if len(straat_vals) > 1:
            for straat_val_x in straat_vals:
                reference_id = straat_val_x.huisnummers[0].id if straat_val_x.huisnummers else None
                postkanton = crab_gateway.get_postkanton_by_huisnummer(reference_id) if reference_id else None
                if postkanton and postcode == str(postkanton.id):
                    straat_val = straat_val_x
                    break
        return straat_val


def process_huisnummer(adres, huisnummer_id, huisnummer, straat_val):
    num_val = None
    if straat_val:
        if huisnummer_id:
            num_val = next((n for n in straat_val.huisnummers if n.id == huisnummer_id), None)
            if num_val:
                adres['huisnummer'] = "" + num_val.huisnummer
        if not huisnummer_id and huisnummer:
            num_val = next(
                (n for n in straat_val.huisnummers if n.huisnummer.lower() == huisnummer.lower()),
                None)
            if num_val:
                adres['huisnummer_id'] = num_val.id
    return num_val


def process_subadres(adres, subadres_id, subadres, num_val):
    subadres_val = None
    if num_val:
        if subadres_id:
            subadres_val = next((sa for sa in num_val.subadressen if sa.id == subadres_id),
                                None)
            if subadres_val:
                adres['subadres'] = "" + subadres_val.subadres
        if not subadres_id and subadres:
            subadres_val = next(
                (sa for sa in num_val.subadressen if sa.subadres.lower() == subadres.lower()),
                None)
            if subadres_val:
                adres['subadres_id'] = subadres_val.id
    return subadres_val


class CrabAdresSchemaNode(colander.MappingSchema):
    id = colander.SchemaNode(
        colander.Integer(),
        missing=None
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

    gemeente = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(1, 50),
        missing=None
    )

    gemeente_id = colander.SchemaNode(
        colander.Integer(),
        missing=None
    )

    land = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(1, 100),
        missing='BE'
    )

    def preparer(self, adres):
        if adres is None or not adres:
            return null  # pragma: no cover
        request = self.bindings['request']
        crab_gateway = request.crab_gateway()
        if 'land' in adres and adres.get('land').upper() == 'BE':
            if adres.get('gemeente_id', None) is None:
                if adres.get('gemeente', None) is None:
                    return None
                gemeente = adres.get('gemeente')
                gewest_ids = [2, 1, 3]
                for gewest_id in gewest_ids:
                    gemeenten = crab_gateway.list_gemeenten(gewest_id)
                    gemeente_val = next((g for g in gemeenten if g.naam.lower() == gemeente.lower()), None)
                    if gemeente_val:
                        adres['gemeente'] = "" + gemeente_val.naam
                        adres['gemeente_id'] = gemeente_val.id
                        break
                if adres.get('gemeente_id', None) is None:
                    return adres
            gemeente_id = adres.get('gemeente_id')
            straat_id = adres.get('straat_id', None)
            straat = adres.get('straat', None)
            huisnummer_id = adres.get('huisnummer_id', None)
            huisnummer = adres.get('huisnummer', None)
            subadres_id = adres.get('subadres_id', None)
            subadres = adres.get('subadres', None)
            try:
                gemeente = crab_gateway.get_gemeente_by_id(gemeente_id)
            except (GatewayRuntimeException, GatewayResourceNotFoundException, AttributeError):
                adres['gemeente'] = None
                return adres
            if gemeente:
                adres['gemeente'] = "" + gemeente.naam
                if straat_id:
                    straat_val = next((s for s in gemeente.straten if s.id == straat_id), None)
                    if straat_val:
                        adres['straat'] = "" + straat_val.label
                        num_val = process_huisnummer(adres, huisnummer_id, huisnummer, straat_val)
                        if num_val:
                            process_subadres(adres, subadres_id, subadres, num_val)
                if not straat_id and straat:
                    straat_val = process_straat(adres, straat, gemeente, crab_gateway)
                    if straat_val:
                        adres['straat_id'] = straat_val.id
                        num_val = process_huisnummer(adres, huisnummer_id, huisnummer, straat_val)
                        if num_val:
                            process_subadres(adres, subadres_id, subadres, num_val)

        else:
            adres['gemeente_id'] = None
            adres['straat_id'] = None
            adres['huisnummer_id'] = None
            adres['subadres_id'] = None
        if 'land' in adres:
            adres['land'] = adres.get('land').upper()
        return adres

    def validator(self, node, adres):
        if not adres:
            return
        request = self.bindings['request']
        crab_gateway = request.crab_gateway()
        if 'land' in adres:
            land = adres.get('land')
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
                gemeente = adres.get('gemeente', None)
                gemeente_id = adres.get('gemeente_id', None)
                straat_id = adres.get('straat_id', None)
                huisnummer_id = adres.get('huisnummer_id', None)
                postcode = adres.get('postcode', None)
                subadres_id = adres.get('subadres_id', None)
                if gemeente_id is None:
                    raise colander.Invalid(
                        node,
                        'geen correcte gemeente_id gevonden voor de gemeente {0}'.format(gemeente)
                    )
                if gemeente is None:
                    raise colander.Invalid(
                        node,
                        'ongeldig gemeente_id {0}'.format(gemeente_id)
                    )
                if straat_id is not None:
                    gemeente = crab_gateway.get_gemeente_by_id(gemeente_id)
                    try:
                        straat = crab_gateway.get_straat_by_id(straat_id)
                    except (GatewayRuntimeException, GatewayResourceNotFoundException, AttributeError):
                        raise colander.Invalid(
                            node,
                            'ongeldig straat_id'
                        )
                    if straat.gemeente_id != gemeente_id:
                        raise colander.Invalid(
                            node,
                            'de straat %s met id %s ligt niet in gemeente %s' %
                            (adres.get('straat', ''), straat_id, gemeente.naam)
                        )
                    if huisnummer_id is not None:
                        try:
                            huisnummer = crab_gateway.get_huisnummer_by_id(huisnummer_id)
                        except (GatewayRuntimeException, GatewayResourceNotFoundException, AttributeError):
                            raise colander.Invalid(
                                node,
                                'ongeldig huisnummer_id'
                            )
                        if huisnummer.straat_id != straat_id:
                            raise colander.Invalid(
                                node,
                                'het huisnummer %s met id %s ligt niet in straat %s' %
                                (adres.get('huisnummer', ''), huisnummer_id, straat.label)
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
                            except (GatewayRuntimeException, GatewayResourceNotFoundException, AttributeError):
                                raise colander.Invalid(
                                    node,
                                    'ongeldig subadres_id'
                                )
                            if subadres.huisnummer_id != huisnummer_id:
                                raise colander.Invalid(
                                    node,
                                    'het subadres %s met id %s ligt niet op huisnummer %s' %
                                    (adres.get('subadres', ''), subadres_id, huisnummer.huisnummer)
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

