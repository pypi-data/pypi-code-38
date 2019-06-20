# -*- coding: utf-8 -*-

from omxware import omxware
from omxware.config import Connection

from omxware.entities.Entity import Entity
from omxware.utils.ResultUtils import list2str


class Ipr(Entity):
    """OMXWare IPR Entity Class"""

    _category = None  # str
    _description = None  # []

    def __init__(self, connecthdr: Connection, ipr):
        """Constructor"""

        """
        {id, name, type, json} attributes are read by the super().constructor()
        So just parse and load the remaining attributes
        """
        super().__init__(connecthdr, ipr)

        if isinstance(ipr, dict):
            self._json = ipr

            # extracting the category for this go
            if 'category' not in ipr:
                self._is_preview_obj = True
            else:
                self._is_preview_obj = False
                self._category = ipr['category']
                self._description = ipr['description']

    def __reload(self):
        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        params = {'page_size': 1, 'page_number': 1}

        if self.id() is not None:
            methodurl = '/api/public/' + self.type() + '/id:'

            if isinstance(self.id(), list):
                methodurl = methodurl + list2str(self.id())

            if isinstance(self.id(), str):
                methodurl = methodurl + self.id()

            resp = self._connecthdr.get(methodurl=methodurl, headers=headers, payload=params)
            results = resp.results()

            if results is not None:
                result = results[0]
                g = Ipr(self._connecthdr, result.json())
                self.__copy(g)

    def __copy(self, ipr):
        self._is_preview_obj = ipr.is_preview_obj()
        self._connecthdr = ipr.connection()
        self._config = ipr.configuration()
        self._omx_token = ipr.omx_token()

        self._json = ipr.json()

        self._id = ipr.id()
        self._type = ipr.type()
        self._name = ipr.name()

        self._category = ipr.category()
        self._description = ipr.description()

    def category(self):
        """
        Get this IPR Code's category

        Returns:
            :return: str :   IPR code's category
        """
        return self._category

    def description(self):
        """
        Get this IPR Code's description

        Returns:
            :return: str :   IPR code's description
        """
        return self._description

    def genes(self,
              page_size=Entity._PAGE_SIZE_DEFAULT,
              page_number=Entity._PAGE_INDEX_DEFAULT
              ):
        """
        Get OMXWare Genes for this IPR code

        Parameters:
            :param page_number: Page Number
            :type page_number: int

            :param page_size: Results page size
            :type page_size: int

        Returns:
            :return:    OmxResponse: Genes
        """
        omx = omxware.omxware(self.connection().config().token(), env=self.connection().config().env())
        results = omx.genes(ipr_ids=self.id(), page_size=page_size, page_number=page_number)

        return results

    def proteins(self,
                 page_size=Entity._PAGE_SIZE_DEFAULT,
                 page_number=Entity._PAGE_INDEX_DEFAULT
                 ):
        """
        Get OMXWare Proteins for this IPR code

        Parameters:
            :param page_number: Page Number
            :type page_number: int

            :param page_size: Results page size
            :type page_size: int

        Returns:
            :return:    OmxResponse: Proteins
        """
        omx = omxware.omxware(self.connection().config().token(), env=self.connection().config().env())
        results = omx.proteins(ipr_ids=self.id(), page_size=page_size, page_number=page_number)

        return results

    def domains(self,
                page_size=Entity._PAGE_SIZE_DEFAULT,
                page_number=Entity._PAGE_INDEX_DEFAULT
                ):
        """
        Get OMXWare Domains for this IPR code

        Parameters:
            :param page_number: Page Number
            :type page_number: int

            :param page_size: Results page size
            :type page_size: int

        Returns:
            :return:    OmxResponse: Domains
        """
        omx = omxware.omxware(self.connection().config().token(), env=self.connection().config().env())
        results = omx.domains(ipr_ids=self.id(), page_size=page_size, page_number=page_number)

        return results
