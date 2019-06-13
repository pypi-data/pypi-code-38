import base64

from django.conf import settings
from django.urls import reverse


def create_dict_from_cmis_doc(cmis_doc):
    properties = cmis_doc.getProperties()

    # Values that need some parsing.
    creatiedatum = properties.get("drc:document__creatiedatum")
    if creatiedatum:
        creatiedatum = creatiedatum.date()

    ontvangstdatum = properties.get("drc:document__ontvangstdatum")
    if ontvangstdatum:
        ontvangstdatum = ontvangstdatum.date()

    verzenddatum = properties.get("drc:document__verzenddatum")
    if verzenddatum:
        verzenddatum = verzenddatum.date()

    ondertekening_datum = properties.get("drc:document__ondertekeningdatum")
    if ondertekening_datum:
        ondertekening_datum = ondertekening_datum.date()

    integriteit_datum = properties.get("drc:document__integriteitdatum")
    if integriteit_datum:
        integriteit_datum = integriteit_datum.date()

    identificatie = properties.get("drc:document__identificatie")

    cmis_id = properties.get("cmis:versionSeriesId").split('/')[-1]

    try:
        inhoud = base64.b64encode(cmis_doc.getContentStream().read()).decode("utf-8")
    except AssertionError:
        return None
    else:
        url = "{}{}".format(settings.HOST_URL, reverse(
            'enkelvoudiginformatieobjecten-detail', kwargs={'version': '1', 'uuid': cmis_id}
        ))
        return {
            "url": url,
            "inhoud": url,
            "creatiedatum": creatiedatum,
            "ontvangstdatum": ontvangstdatum,
            "verzenddatum": verzenddatum,
            "integriteit_datum": integriteit_datum,
            "ondertekening_datum": ondertekening_datum,
            "titel": properties.get("cmis:name"),
            "identificatie": identificatie,
            "bronorganisatie": properties.get("drc:document__bronorganisatie"),
            "vertrouwelijkaanduiding": properties.get("drc:document__vertrouwelijkaanduiding"),
            "auteur": properties.get("drc:document__auteur"),
            "status": properties.get("drc:document__status"),
            "beschrijving": properties.get("drc:document__beschrijving"),
            "indicatie_gebruiksrecht": properties.get("drc:document__indicatiegebruiksrecht"),
            "ondertekening_soort": properties.get("drc:document__ondertekeningsoort"),
            "informatieobjecttype": properties.get("drc:document__informatieobjecttype"),
            "formaat": properties.get("drc:document__formaat"),
            "taal": properties.get("drc:document__taal"),
            "bestandsnaam": properties.get("drc:document__bestandsnaam"),
            "link": properties.get("drc:document__link"),
            "integriteit_algoritme": properties.get("drc:document__integriteitalgoritme"),
            "integriteit_waarde": properties.get("drc:document__integriteitwaarde"),
            "bestandsomvang": len(inhoud),
        }


def create_case_dict_from_cmis_doc(cmis_doc):
    properties = cmis_doc.getProperties()

    cmis_id = properties.get("cmis:versionSeriesId").split('/')[-1]
    url = "{}{}".format(settings.HOST_URL, reverse(
        'objectinformatieobjecten-detail', kwargs={'version': '1', 'uuid': cmis_id}
    ))
    eio_url = "{}{}".format(settings.HOST_URL, reverse(
        'enkelvoudiginformatieobjecten-detail', kwargs={'version': '1', 'uuid': cmis_id}
    ))

    return {
        "url": url,
        "informatieobject": eio_url,
        "object": properties.get('drc:connectie__zaakurl'),
        "object_type": properties.get("drc:connectie__objecttype"),
        "aard_relatie_weergave": properties.get("drc:connectie__aardrelatieweergave"),
        "titel": properties.get("drc:connectie__titel"),
        "beschrijving": properties.get("drc:connectie__beschrijving"),
        "registratiedatum": properties.get("drc:connectie__registratiedatum"),
    }
