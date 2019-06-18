from ms_sdk.Resourses import Resource


class InvoicesResource(Resource):
    """
    Class InvoicesResource
    :method Invoice get(int id):
    :method Invoice first():
    :method Invoice[] all():
    :method Invoice update(id, data):
    :method Invoice create(data):
    """

    def getURI(self):
        return 'invoices'