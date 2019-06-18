from ms_sdk.Exceptions.MethodNotFoundException import MethodNotFoundException
from ms_sdk.Lib.Helpers.ClassReflectionHelper import ClassReflectionHelper
from ms_sdk.Resourses import Resource


class CorrelationsResource(Resource):

    def getURI(self):
        return 'correlations'

    def getById(self, id, forClassName):
        """
        :param id:
        :param forClassName:
        :return dict|Collection:
        """
        params = self.getQueryParams()

        caseType = ClassReflectionHelper(forClassName).getShortLowerCaseName()
        uriAppend = '{}/{}'.format(caseType, id)

        response = self.handler.handle('GET', False, uriAppend, params)
        return self.make(response)

    def get(self, id: int):
        """
        :param int id:
        :raises MethodNotFoundException:
        """
        raise MethodNotFoundException('Method get() can not be use with correlations')

    def update(self, id: int, data):
        """
        :param int id:
        :param data:
        :raises MethodNotFoundException:
        """
        raise MethodNotFoundException('Method update() can not be use with correlations')

    def create(self, data):
        """
        :param data:
        :raises MethodNotFoundException:
        """
        raise MethodNotFoundException('Method create() can not be use with correlations')

    def delete(self, id: int):
        """
        :param int id:
        :raises MethodNotFoundException:
        """
        raise MethodNotFoundException('Method delete() can not be use with correlations')