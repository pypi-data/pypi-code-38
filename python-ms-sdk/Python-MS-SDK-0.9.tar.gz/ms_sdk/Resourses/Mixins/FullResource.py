from ms_sdk.Exceptions.EntityNotFoundException import EntityNotFoundException


class FullResourceMixin:

    def fullAll(self):
        """
        :return Entity[]:
        """
        return self.full()

    def fullById(self, id):
        """
        :param id:
        :raises EntityNotFoundException:
        :return Entity:
        """
        all = self.full(id)
        return self.checkAndReturnResult(all)

    def fullByCode(self, code):
        """
        :param code:
        :raises EntityNotFoundException:
        :return Entity:
        """
        all = self.full(code)
        return self.checkAndReturnResult(code)

    def full(self, param=None):
        """
        Get list of entities
        :param None|int|string param:
        :return Entity|Entity[]:
        """
        uriAppend = 'full'
        params = self.getQueryParams()

        if param:
            if isinstance(param, type(1)):
                uriAppend = uriAppend + '/' + str(param)
            else:
                uriAppend = 'url/' + str(param)

        response = self.handler.handle('GET', False, uriAppend, params)
        return self.make(response)

    def checkAndReturnResult(self, all):
        """
        :raises EntityNotFoundException:
        :param all:
        :return Entity:
        """
        try:
            if all[0]:
                return all[0]
        except:
            if not all:
                EntityNotFoundException('Entity full with was not found!')
        return all