from ms_sdk.Exceptions.MethodNotFoundException import MethodNotFoundException
from ms_sdk.Lib.Filters.Grid.GridFilter import GridFilter
from ms_sdk.Lib.Makers.CountMaker import CountMaker
from ms_sdk.Lib.Makers.FacetsMaker import FacetsMaker
from ms_sdk.Lib.Specifications.Basic.FilterSpecification import FilterSpecification
from ms_sdk.Resourses import Resource


class GridResource(Resource):

    def getURI(self):
        return 'grid'

    def filter(self, gFilter):
        """
        Set filter to the resource selecting
        :param dict|FilterSpecification|GridFilter gFilter:
        :return self:
        """
        if type(gFilter) == dict:
            gFilter = GridFilter(gFilter)

        if isinstance(type(gFilter), FilterSpecification):
            gFilter = GridFilter(gFilter.asFilter())

        self.__filter = filter
        return self

    def all(self):
        """
        :return Entity{}|Collection:
        """
        params = self.getQueryParams()
        response = self.handler.handle('GET', False, False, params)
        return self.make(response)

    def facets(self):
        """
        :return Entity{}|Collection:
        """
        params = self.getQueryParams()
        response = self.handler.handle('GET', False, 'filter', params)
        return self.make(response, False, FacetsMaker())

    def count(self):
        """
        :rtype int:
        """
        params = self.getQueryParams()
        response = self.handler.handle('GET', False, 'count', params)
        return self.make(response, False, CountMaker())

    def get(self, id):
        """
        :raises MethodNotFoundException:
        :param id:
        """
        raise MethodNotFoundException('Method get() can not be use with GRID')

    def update(self, id, data):
        """
        :raises MethodNotFoundException:
        :param id:
        :param data:
        """
        raise MethodNotFoundException('Method update() can not be use with GRID')

    def create(self, data):
        """
        :raises MethodNotFoundException:
        :param data:
        """
        raise MethodNotFoundException('Method create() can not be use with GRID')

    def delete(self, id):
        """
        :raises MethodNotFoundException:
        :param id:
        """
        raise MethodNotFoundException('Method delete() can not be use with GRID')

    def getQueryParams(self):
        """
        TODO: move to GrapherResource
        :return dict|mixed:
        """
        params = Resource.getQueryParams(self)

        try:
            if not params['where']:
                return params
        except:
            return params

        for where in params['where'].split('&'):
            pairs = where.split('=')

            for pair in pairs:
                temp = pair.split('=')
                params[temp[0]] = temp[1]

            del params['where']
        return params