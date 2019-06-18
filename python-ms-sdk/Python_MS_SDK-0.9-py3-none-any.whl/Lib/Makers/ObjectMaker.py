from ms_sdk.Exceptions.EntityNotFoundException import EntityNotFoundException
from ms_sdk.Lib.Collection import Collection
from ms_sdk.Lib.Http.Meta import Meta
from ms_sdk.Lib.Http.Response import Response
from ms_sdk.Lib.Mappers import *
from ms_sdk.Entities.Entity import Entity
from ms_sdk.Lib.Makers.Maker import *


class ObjectMaker(Maker):

    def makeArray(self, response: Response):
        """
        :param Response response:
        :raises EntityNotFoundException:
        :rtype list|Collection:
        """
        if not response.getSuccess():
            return Collection([], Meta())

        result = self.getResultFromResponse(response)

        if self.asCollection:
            collection = Collection(result, response.getMeta())
            return collection
        return result

    def makeSingle(self, response: Response):
        """
        :param Response response:
        :rtype None|Entity:
        """
        if not response.getSuccess():
            return None

        result = self.getResultFromResponse(response)
        return result or None

    def getMapperClass(self, mapperType):
        """
        :param mapperType:
        :rtype None|string:
        """
        try:
            return eval(mapperType[0].upper() + mapperType[1:] + 'Mapper.' +
                        mapperType[0].upper() + mapperType[1:] + 'Mapper')
        except Exception:
            return None

    def getAttributes(self, element):
        """
        :param dict element:
        :rtype dict:
        """
        if element['attributes'] and isinstance(element['attributes'], dict):
            return element['attributes']
        return {}

    def getRelationships(self, element, included):
        """
        :param dict element:
        :param dict included:
        :raises EntityNotFoundException:
        :rtype dict:
        """
        if not element['relationships'] and not isinstance(
                element['relationships'], dict):
            return {}

        result = {}

        for (relationKey, relationValue) in element['relationships'].items():
            for relationData in relationValue['data']:
                try:
                    if not relationData['id'] in included[relationData['type']]:
                        raise KeyError
                except KeyError:
                    raise EntityNotFoundException('Data for type[' + relationData['type'] + ' ] and id[' + relationData[
                        'id'] + '] was not found in includes')

                result.update({relationKey: included[relationData['type']]})
        return result

    def getIncludedArray(self, included):
        """
        Prepare array of included data, we walk through ONCE
        result example: ['brands'][706] = {attributes}
        :param included:
        :rtype dict:
        """
        result = {}

        if not included:
            return result

        for include in included:
            try:
                result[include['type']].update(
                    {include['id']: include['attributes']})
            except BaseException:
                result.update(
                    {include['type']: {include['id']: include['attributes']}})
        return result

    def getResultFromResponse(self, response: Response):
        """
        :raises EntityNotFoundException:
        :param Response response:
        :rtype dict:
        """
        result = []
        included = self.getIncludedArray(response.getIncluded())

        for element in response.getData():
            mapperClass = self.getMapperClass(element['type'])

            if not mapperClass:
                raise EntityNotFoundException('Entity mapper class for ' + element['type'] + ' was not found')

            result.append(self.createObject(mapperClass, element, included))

        if len(result) == 1:
            return result[0]
        return result

    def createObject(self, mapperClass, element, included):
        """
        :param mapperClass:
        :param element:
        :param included:
        :rtype mixed:
        """
        item = self.getAttributes(element)
        relations = self.getRelationships(element, included)

        try:
            item.update(included)
        except BaseException:
            item.append(relations)

        mapper = mapperClass()
        return mapper.createObject(item)
