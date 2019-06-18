import base64
from datetime import datetime

from django.conf import settings
from django.urls import reverse

from .mapper import reverse_mapper


def create_dataclass_from_cmis_doc(cmis_doc, dataclass):
    properties = cmis_doc.getProperties()

    try:
        inhoud = base64.b64encode(cmis_doc.getContentStream().read()).decode("utf-8")
    except AssertionError:
        return None
    else:
        cmis_id = properties.get("cmis:versionSeriesId").split("/")[-1]
        url = f"{settings.HOST_URL}{reverse('enkelvoudiginformatieobjecten-detail', kwargs={'version': '1', 'uuid': cmis_id})}"
        download_url = f"{settings.HOST_URL}{reverse('cmis:cmis_download', kwargs={'uuid': cmis_id})}"

        obj_dict = {reverse_mapper(key): value for key, value in properties.items() if reverse_mapper(key)}
        # remove verwijderd
        del obj_dict["verwijderd"]

        # Correct datetimes to dates
        for key, value in obj_dict.items():
            if isinstance(value, datetime):
                obj_dict[key] = value.date()

        # These values are not in alfresco
        obj_dict["url"] = url
        obj_dict["inhoud"] = download_url
        obj_dict["bestandsomvang"] = len(inhoud)
        return dataclass(**obj_dict)


def create_case_dict_from_cmis_doc(cmis_doc):
    properties = cmis_doc.getProperties()

    cmis_id = properties.get("cmis:versionSeriesId").split("/")[-1]
    url = "{}{}".format(settings.HOST_URL, reverse("objectinformatieobjecten-detail", kwargs={"version": "1", "uuid": cmis_id}))
    eio_url = "{}{}".format(settings.HOST_URL, reverse("enkelvoudiginformatieobjecten-detail", kwargs={"version": "1", "uuid": cmis_id}))

    return {
        "url": url,
        "informatieobject": eio_url,
        "object": properties.get("drc:connectie__zaakurl"),
        "object_type": properties.get("drc:connectie__objecttype"),
        "aard_relatie_weergave": properties.get("drc:connectie__aardrelatieweergave"),
        "titel": properties.get("drc:connectie__titel"),
        "beschrijving": properties.get("drc:connectie__beschrijving"),
        "registratiedatum": properties.get("drc:connectie__registratiedatum"),
    }
