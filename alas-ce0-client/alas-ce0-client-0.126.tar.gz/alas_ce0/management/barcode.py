from alas_ce0.common.client_base import EntityClientBase


class BarcodeClient(EntityClientBase):
    entity_endpoint_base_url = '/management/barcodes/'

    def authenticate(self, barcode_name, password):
        return self.http_post_json(self.entity_endpoint_base_url + '_authenticate',
                                   {'barcode_name': barcode_name, 'password': password})

    def reset_password(self, barcode_name, password):
        return self.http_post_json(self.entity_endpoint_base_url + '_reset-password',
                                   {'barcode_name': barcode_name, 'password': password})
