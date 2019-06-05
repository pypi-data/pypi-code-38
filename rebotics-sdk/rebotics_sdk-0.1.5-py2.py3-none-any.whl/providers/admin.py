from .base import ReboticsBaseProvider, remote_service


class AdminProvider(ReboticsBaseProvider):
    @remote_service('/admin/', json=False)
    def admin_ping(self, **kwargs):
        return self.session.get()

    @remote_service('/nn_models/tf/models/')
    def get_retailer_tf_models(self):
        return self.session.get()

    @remote_service('/retailers/host/')
    def get_retailer(self, retailer_codename):
        response = self.session.post(data={
            'company': retailer_codename
        })
        return response

    def get_retailer_host(self, retailer_codename):
        return self.get_retailer(retailer_codename)['host']

    @remote_service('/retailers/')
    def get_retailer_list(self):
        return self.session.get()

    def set_retailer_identifier(self, retailer_id, retailer_secret_key):
        self.headers['x-retailer-id'] = retailer_id
        self.headers['x-retailer-secret-key'] = retailer_secret_key
