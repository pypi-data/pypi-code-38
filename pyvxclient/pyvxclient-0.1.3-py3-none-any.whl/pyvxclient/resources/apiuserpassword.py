from pyvxclient.resource import Resource


class ApiUserPassword(Resource):

    def get(self, username_or_email, portal_url):
        return self.client.api.getApiPassword(username_or_email=username_or_email, url=portal_url).response().result
