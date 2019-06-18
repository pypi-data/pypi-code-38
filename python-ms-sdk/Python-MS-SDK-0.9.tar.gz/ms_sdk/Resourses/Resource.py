import json
from ms_sdk.Exceptions.EntityNotFoundException import EntityNotFoundException
from ms_sdk.Lib.Makers.CountMaker import CountMaker
from ms_sdk.Lib.Specifications.Basic.IsVisible import IsVisible
from ms_sdk.Lib.Http.Request import Request
from ms_sdk.Lib.Http.Response import Response
from ms_sdk.Lib.Makers.ObjectMaker import ObjectMaker
from ms_sdk.Lib.Makers.Maker import Maker
from ms_sdk.Lib.Filters.Filter import Filter


class Resource:
    _fields = []
    _offset = 0
    _filter = ''
    _limit = 10
    _sort = []
    _ids = []
    _in = {}
    _meta = False

    def __init__(self, client: object, version: str = '') -> object:
        """
        BaseService initializer
        :param client:
        :param str version:
        """
        self.client = client
        self.version = version or client.getVersion()
        self.handler = Request(self.client, self)
        self.maker = ObjectMaker()

        # Reset params
        self.resetData()

    def limit(self, _limit: int = 10, offset: int = 0):
        """
        Set a limit on the number of resource and offset for skipping the number of resource
        :param _limit:
        :param offset:
        :return: self
        """
        self._limit = _limit
        self._offset = offset

        return self

    def getLimit(self):
        """
        Get the resource limit
        :rtype: int
        """
        return self._limit

    def getOffset(self) -> int:
        """
        Get the resource offset
        :rtype: int
        """
        return self._offset

    def delete(self, id):
        response = self.handler.handle('DELETE', False, id)

        if not response.getSuccess():
            raise response.getErrorMessage()

        return response.getSuccess()

    def create(self, data):
        response = self.handler.handle('POST', body=True, queryParams=data)

        if not response.getSuccess():
            print(response.getData())
            raise response.getErrorMessage()

        return self.make(response, False)

    def update(self, id, data):
        response = self.handler.handle('PUT', data, id)

        if not response.getSuccess():
            raise EntityNotFoundException(response.getErrorMessage())

        return self.make(response, False)

    def ids(self, ids: list) -> object:
        """
        Set list of ids for selecting list of resources
        :param ids:
        :return: self
        """
        self._ids = []

        if type(ids) == list:
            self._ids = ids
        else:
            self._ids.append(str(ids))

        return self

    def getIds(self) -> list:
        """
        Get list of ids for selecting list of resources
        :rtype: list
        """
        return self._ids

    def byIn(self, field, values):
        """
        :param field:
        :param values:
        :return: self
        """
        self._in = {field : values}
        return self

    def sort(self, field) -> object:
        """
        Set field for sorting
        :param field:
        :return: self
        """
        self._sort.append(field)
        return self

    def getSort(self) -> list:
        """
        Get fields for sorting
        :rtype: list
        """
        return self._sort

    def resetSort(self):
        """
        Reset sorting
        """
        self._sort = []

    def fields(self, fields: list) -> object:
        """
        Set list of fields for selecting the resource
        :return: self
        """
        self._fields = fields
        return self
    
    def getFields(self) -> list:
        """
        Get list of fields for selecting the resources
        :rtype: list
        """
        return self._fields

    def filter(self, _filter) -> object:
        """
        Set filter to the resource selecting
        :param list|Filter|FilterSpecification _filter:
        :return: self
        """
        try:
            if len(_filter._elements) >= 1:
                self._filter = Filter(_filter._elements)
        except:
            if type(_filter) == IsVisible:
                self._filter = Filter(_filter.asFilter())
            else:
                self._filter = Filter(_filter)

        return self

    def getFilter(self) -> Filter:
        """
        Get current filter
        :rtype: Filter
        """
        return self._filter.getFilters()

    def resetFilters(self):
        """
        Reset current filters
        """
        try:
            self._filter.filters = {}
        except:
            self._filter = None
        return self

    def withMeta(self) -> object:
        """
        :return: self
        """
        self._meta = True
        return self

    def get(self, id: int):
        """
        Get entity by id
        :param id:
        :rtype: list
        """
        if not id:
            return print('Id is not specified')

        params = {}

        if self._fields:
            params['fields'] = ','.join(self._fields)

        response = self.handler.handle('GET', False, str(id), params)
        return self.make(response, False)

    def all(self):
        """
        Get list of entities
        :rtype: list
        """
        params = self.getQueryParams()
        response = self.handler.handle('GET', False, 'by', params)
        return self.make(response, False)

    def first(self):
        """
        Get first entity - limit = 1
        :rtype: Entity|None
        """
        self.limit(1, 0)
        params = self.getQueryParams()

        response = self.handler.handle('GET', False, 'by', params)
        return self.make(response, False)

    def count(self):
        """
        :rtype: int
        """
        params = self.getQueryParams()
        response = self.handler.handle('GET', False, 'count', params)
        return self.make(response, False, CountMaker())

    def make(self, response, makeArray: bool=True, maker: Maker = None):
        """
        :param response: Promise|Response $response
        :param makeArray:
        :param maker:
        :rtype: list|Collection|Entity|int
        """
        if not maker:
            maker = self.maker
        maker.setAsCollection(self._meta)

        if isinstance(response, Response):
            # TODO: add afterAPICall
            if makeArray:
                return maker.makeArray(response)

            return maker.makeSingle(response)
        return {'response': response, 'maker': maker, 'makeArray': makeArray}

    def getQueryParams(self):
        """
        :rtype: list
        """
        params = {
            'offset': self._offset,
            'limit': self._limit
        }

        if self._ids:
            params['ids'] = ','.join(self._ids)
        if self._fields:
            params['fields'] = ','.join(self._fields)
        if self._sort:
            params['sort'] = ','.join(self._sort)
        if self._filter:
            params['where'] = self._filter.toString()
        if self._in:
            params['in'] = json.dumps(self._in)

        return params

    def resetData(self):
        """
        Reset data when initialization
        """
        self._fields = []
        self._offset = 0
        self._filter = ''
        self._limit = 10
        self._sort = []
        self._ids = {}
        self._in = {}