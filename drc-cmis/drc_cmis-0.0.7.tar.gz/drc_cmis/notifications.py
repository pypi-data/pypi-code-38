"""
Listen to the notifications that are send by the NRC
"""
from vng_api_common.models import APICredential
from vng_api_common.notifications.handlers import RoutingHandler, auth, log
from zds_client.client import Client

from drc_cmis.client import cmis_client


class ZakenHandler:
    def handle(self, data: dict) -> None:
        if data.get('actie') == 'create' and data.get('resource') == 'zaak':
            zaaktype_url = data.get('kenmerken', {}).get('zaaktype')
            client = Client.from_url(zaaktype_url)
            client.auth = APICredential.get_auth(zaaktype_url)
            zaaktype_data = client.retrieve('zaaktype', url=zaaktype_url)
            print(zaaktype_data)
            zaaktype_folder = cmis_client.get_or_create_zaaktype_folder(zaaktype_data)

            zaak_url = data.get('resource_url')
            client = Client.from_url(zaak_url)
            client.auth = APICredential.get_auth(zaak_url)
            zaak_data = client.retrieve('zaak', url=zaak_url)
            print(zaak_data)
            cmis_client.get_or_create_zaak_folder(zaak_data, zaaktype_folder)


default = RoutingHandler({'autorisaties': auth, 'zaken': ZakenHandler()}, default=log)
