from ms_sdk.Resourses import Resource


class CompaniesResource(Resource):
    """
    Class CompanysResource
    :method Company get(int id):
    :method Company first():
    :method Company[] all():
    :method Company update(id, data):
    :method Company create(data):
    """

    def getURI(self):
        return 'companies'