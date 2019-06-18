ZAAKTYPE_MAP = {"url": "drc:zaaktype__url", "identificatie": "drc:zaaktype__identificatie"}

ZAAK_MAP = {
    "url": "drc:zaak__url",
    "identificatie": "drc:zaak__identificatie",
    "zaaktype": "drc:zaak__zaaktypeurl",
    "bronorganisatie": "drc:zaak__bronorganisatie",
}


DOCUMENT_MAP = {
    # "uuid": "drc:",
    "identificatie": "drc:document__identificatie",
    "bronorganisatie": "drc:document__bronorganisatie",
    "creatiedatum": "drc:document__creatiedatum",
    "titel": "cmis:name",
    "vertrouwelijkheidaanduiding": "drc:document__vertrouwelijkaanduiding",
    "auteur": "drc:document__auteur",
    "status": "drc:document__status",
    "beschrijving": "drc:document__beschrijving",
    "ontvangstdatum": "drc:document__ontvangstdatum",
    "verzenddatum": "drc:document__verzenddatum",
    "indicatie_gebruiksrecht": "drc:document__indicatiegebruiksrecht",
    "ondertekening_soort": "drc:document__ondertekeningsoort",
    "ondertekening_datum": "drc:document__ondertekeningdatum",
    "informatieobjecttype": "drc:document__informatieobjecttype",
    "formaat": "drc:document__formaat",
    "taal": "drc:document__taal",
    "bestandsnaam": "drc:document__bestandsnaam",
    # "inhoud": "drc:",
    "link": "drc:document__link",
    "integriteit_algoritme": "drc:document__integriteitalgoritme",
    "integriteit_waarde": "drc:document__integriteitwaarde",
    "integriteit_datum": "drc:document__integriteitdatum",
    "verwijderd": "drc:document__verwijderd",
}

CONNECTION_MAP = {
    "object": "drc:connectie__zaakurl",
    "objectType": "drc:connectie__objecttype",
    "aardRelatieWeergave": "drc:connectie__aardrelatieweergave",
    "titel": "drc:connectie__titel",
    "beschrijving": "drc:connectie__beschrijving",
    "registratieDatum": "drc:connectie__registratiedatum",
}

REVERSE_ZAAKTYPE_MAP = {value: key for key, value in ZAAKTYPE_MAP.items()}
REVERSE_ZAAK_MAP = {value: key for key, value in ZAAK_MAP.items()}
REVERSE_DOCUMENT_MAP = {value: key for key, value in DOCUMENT_MAP.items()}
REVERSE_CONNECTION_MAP = {value: key for key, value in CONNECTION_MAP.items()}


def mapper(drc_name, type="document"):
    if type == "document":
        return DOCUMENT_MAP.get(drc_name, None)
    if type == "connection":
        return CONNECTION_MAP.get(drc_name, None)
    if type == "zaaktype":
        return ZAAKTYPE_MAP.get(drc_name, None)
    if type == "zaak":
        return ZAAK_MAP.get(drc_name, None)
    return None


def reverse_mapper(cmis_name, type="document"):
    if type == "document":
        return REVERSE_DOCUMENT_MAP.get(cmis_name, None)
    if type == "connection":
        return REVERSE_CONNECTION_MAP.get(cmis_name, None)
    if type == "zaaktype":
        return REVERSE_ZAAKTYPE_MAP.get(cmis_name, None)
    if type == "zaak":
        return REVERSE_ZAAK_MAP.get(cmis_name, None)
    return None
