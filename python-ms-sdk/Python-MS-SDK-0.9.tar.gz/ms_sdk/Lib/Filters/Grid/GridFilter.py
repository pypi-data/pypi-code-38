import json
import urllib.parse
from ms_sdk.Lib.Filters.Filter import Filter


class GridFilter(Filter):

    _level = 0
    _elements = {}

    def elements(self, elements):
        """
        :param elements: GridFilterElement[]
        :rtype self:
        """
        self._elements[self._level] = {}

        for element in elements:
            self._elements[self._level].update({
                element.getName(): element.getValues()
            })

        self._level += 1
        return self

    def reset(self):
        """
        Reset local vars
        :rtype self:
        """
        self._elements.clear()
        self._level = 0
        return self

    def setFilters(self, filters={}):
        """
        :param list filters:
        :rtype self:
        """
        for key, value in filters:
            self.addFilter(key, value)
        return self

    def addFilter(self, field, value, operator=None):
        """
        Adds a filter to the resource request
        :param field: the field to filter on
        :param value: the value of the attribute to operate on

        :param operator:
        :rtype self:
        """
        self.filters.update({
            field: value
        })
        return self

    def getElements(self):
        """
        :rtype: GridFilterElement
        """
        return self._elements

    def toString(self):
        """
        Convert the filter object to a string for a URL
        :rtype str:
        """
        setParams = self.__getStandardFilter()

        if self._elements:
            setParams['params'] = json.dumps(self._elements)

        strFilter = urllib.parse.unquote_plus(urllib.parse.urlencode(setParams))\
            .replace('={"0": ', '=[')\
            .replace('"1": ', '')\
            .replace('}}', '}]')\
            .replace(' ', '')
        return strFilter

    def __getStandardFilter(self):
        """
        :rtype dict:
        """
        setParams = {}

        if self.filters:
            for key, value in self.filters:
                if isinstance(value, dict):
                    setParams.update({key: ','.join(value)})
                else:
                    setParams.update({key: value})
        return setParams
