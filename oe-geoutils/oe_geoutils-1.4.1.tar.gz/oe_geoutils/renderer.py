# -*- coding: utf-8 -*-


def locatie_element_adapter(obj, request=None):
    '''
    Adapter for rendering
    :class:`oe_geoutils.data.models.LocatieElement` to json.

    Add the adapter to `jsonpublish`
    from jsonpublish import register_adapter
    register_adapter(LocatieElement, locatie_element_adapter)

    Add the adapter to your :class:`pyramid.renderers.JSON` json_renderer
    from pyramid.renderers import JSON
    json_renderer = JSON()
    json_renderer.add_adapter(LocatieElement, locatie_element_adapter)
    '''
    locatie_element = {
        'id': obj.id,
        'type': obj.type,
        'provincie': {
            'niscode': obj.provincie_niscode,
            'naam': obj.provincie_naam
        },
        'gemeente': {
            'niscode': obj.gemeente_niscode,
            'naam': obj.gemeente_naam,
            'id': obj.gemeente_crab_id
        },
        'deelgemeente': {
            'niscode': obj.deelgemeente_niscode,
            'naam': obj.deelgemeente_naam
        }

    }
    return locatie_element


def perceel_adapter(obj, request=None):
    '''
    Adapter for rendering
    :class:`oe_geoutils.data.models.Perceel` to json.

    Add the adapter to `jsonpublish`
    from jsonpublish import register_adapter
    register_adapter(Perceel, perceel_adapter)

    Add the adapter to your :class:`pyramid.renderers.JSON` json_renderer
    from pyramid.renderers import JSON
    json_renderer = JSON()
    json_renderer.add_adapter(Perceel, perceel_adapter)
    '''
    perceel = {
        'id': obj.id,
        'type': obj.type,
        'provincie': {
            'niscode': obj.provincie_niscode,
            'naam': obj.provincie_naam
        },
        'gemeente': {
            'niscode': obj.gemeente_niscode,
            'naam': obj.gemeente_naam,
            'id': obj.gemeente_crab_id
        },
        'deelgemeente': {
            'niscode': obj.deelgemeente_niscode,
            'naam': obj.deelgemeente_naam
        }

    }
    if obj.capakey and len(obj.capakey) > 0:
        perceel.update({
            'perceel': {
                'afdeling': obj.afdeling,
                'sectie': obj.sectie,
                'perceel': obj.perceel,
                'capakey': obj.capakey
            }
        })
    return perceel


def openbaar_domein_adapter(obj, request=None):
    '''
    Adapter for rendering
    :class:`oe_geoutils.data.models.OpenbaarDomein` to json.

    Add the adapter to `jsonpublish`
    from jsonpublish import register_adapter
    register_adapter(OpenbaarDomein, openbaar_domein_adapter)

    Add the adapter to your :class:`pyramid.renderers.JSON` json_renderer
    from pyramid.renderers import JSON
    json_renderer = JSON()
    json_renderer.add_adapter(OpenbaarDomein, openbaar_domein_adapter)
    '''
    openbaar_domein = {
        'id': obj.id,
        'type': obj.type,
        'provincie': {
            'niscode': obj.provincie_niscode,
            'naam': obj.provincie_naam
        },
        'gemeente': {
            'niscode': obj.gemeente_niscode,
            'naam': obj.gemeente_naam,
            'id': obj.gemeente_crab_id
        },
        'deelgemeente': {
            'niscode': obj.deelgemeente_niscode,
            'naam': obj.deelgemeente_naam
        },
        'omschrijving': obj.omschrijving
    }
    return openbaar_domein


def locatie_adres_adapter(obj, request=None):
    '''
    Adapter for rendering
    :class:`oe_geoutils.data.models.LocatieAdres` to json.

    Add the adapter to `jsonpublish`
    from jsonpublish import register_adapter
    register_adapter(LocatieAdres, locatie_adres_adapter)

    Add the adapter to your :class:`pyramid.renderers.JSON` json_renderer
    from pyramid.renderers import JSON
    json_renderer = JSON()
    json_renderer.add_adapter(LocatieAdres, locatie_adres_adapter)
    '''
    locatie_adres = {
        'id': obj.id,
        'type': obj.type,
        'provincie': {
            'niscode': obj.provincie_niscode,
            'naam': obj.provincie_naam
        },
        'gemeente': {
            'niscode': obj.gemeente_niscode,
            'naam': obj.gemeente_naam,
            'id': obj.gemeente_crab_id
        },
        'deelgemeente': {
            'niscode': obj.deelgemeente_niscode,
            'naam': obj.deelgemeente_naam
        },
        'huisnummer_id': obj.huisnummer_id,
        'huisnummer': obj.huisnummer,
        'subadres_id': obj.subadres_id,
        'subadres': obj.subadres,
        'straat': obj.straat,
        'straat_id': obj.straat_id,
        'postcode': obj.postcode,
        'land': obj.land
    }
    return locatie_adres
