MAP = {
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
}

REVERSE_MAP = {
    value: key for key, value in MAP.items()
}

def mapper(drc_name):
    return MAP.get(drc_name, None)


def reverse_mapper(cmis_name):
    return REVERSE_MAP.get(cmis_name, None)
