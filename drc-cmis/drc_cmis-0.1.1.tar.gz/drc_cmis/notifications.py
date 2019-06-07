"""
Listen to the notifications that are send by the NRC
"""
from vng_api_common.models import APICredential
from vng_api_common.notifications.handlers import default
from zds_client.client import Client

from drc_cmis.client import cmis_client


class ZakenHandler:
    def handle(self, data: dict) -> None:
        if data.get('actie') == 'create' and data.get('resource') == 'zaak':
            zaaktype_url = data.get('kenmerken', {}).get('zaaktype')
            client = Client.from_url(zaaktype_url)
            client.auth = APICredential.get_auth(zaaktype_url)
            client.auth.set_claims(scopes=['zds.scopes.zaaktypes.lezen'])
            zaaktype_data = client.retrieve('zaaktype', url=zaaktype_url)
            print(zaaktype_data)
            zaaktype_folder = cmis_client.get_or_create_zaaktype_folder(zaaktype_data)

            zaak_url = data.get('resource_url')
            client = Client.from_url(zaak_url)
            client.auth = APICredential.get_auth(zaak_url)
            client.auth.set_claims(scopes=[
                'notificaties.scopes.publiceren',
                'zds.scopes.statussen.toevoegen',
                'zds.scopes.zaken.aanmaken',
                'zds.scopes.zaken.bijwerken',
                'zds.scopes.zaken.geforceerd-bijwerken',
                'zds.scopes.zaken.heropenen',
                'zds.scopes.zaken.lezen',
                'zds.scopes.zaken.verwijderen',
            ])
            zaak_data = client.retrieve('zaak', url=zaak_url)
            print(zaak_data)
            cmis_client.get_or_create_zaak_folder(zaak_data, zaaktype_folder)


class RoutingHandler:

    def __init__(self, config: dict, default=None):
        self.config = config
        self.default = default

    def handle(self, message: dict):
        handler = self.config.get(message['kanaal'])
        if handler is not None:
            handler.handle(message)
        elif self.default:
            self.default.handle(message)


default = RoutingHandler({'zaken': ZakenHandler()}, default=default)
