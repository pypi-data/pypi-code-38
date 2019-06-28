# -*- coding: utf-8 -*-

from omxware import omxware
from omxware.config import Connection

from omxware.entities.Entity import Entity
from omxware.utils.ResultUtils import list2str


class Go(Entity):
    """OMXWare GO Entity Class"""

    _category = None  # str

    def __init__(self, connecthdr: Connection, go):
        """Constructor"""

        """
        {id, name, type, json} attributes are read by the super().constructor()
        So just parse and load the remaining attributes
        """
        super().__init__(connecthdr, go)

        if isinstance(go, dict):
            self._json = go

            # extracting the category for this go
            if 'category' not in go:
                self._is_preview_obj = True
            else:
                self._is_preview_obj = False
                self._category = go['category']

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
                g = Go(self._connecthdr, result.json())
                self.__copy(g)

    def __copy(self, go):
        self._is_preview_obj = go.is_preview_obj()
        self._connecthdr = go.connection()
        self._config = go.configuration()
        self._omx_token = go.omx_token()

        self._json = go.json()

        self._id = go.id()
        self._type = go.type()
        self._name = go.name()

        self._category = go.category()

    def category(self):
        """
        Get this GO Term's category

        Returns:
            :return: str :   GO Term category
        """
        return self._category

    def genes(self,
              page_size=Entity._PAGE_SIZE_DEFAULT,
              page_number=Entity._PAGE_INDEX_DEFAULT
              ):
        """
        Get OMXWare Genes for this GO Term

        Parameters:
            :param page_number: Page Number
            :type page_number: int

            :param page_size: Results page size
            :type page_size: int

        Returns:
            :return:    OmxResponse: Genes
        """
        omx = omxware.omxware(self.connection().config().token(), env=self.connection().config().env())
        results = omx.genes(go_terms=self.id(), page_size=page_size, page_number=page_number)

        return results

    def proteins(self,
                 page_size=Entity._PAGE_SIZE_DEFAULT,
                 page_number=Entity._PAGE_INDEX_DEFAULT
                 ):
        """
        Get OMXWare Proteins for this GO Term

        Parameters:
            :param page_number: Page Number
            :type page_number: int

            :param page_size: Results page size
            :type page_size: int

        Returns:
            :return:    OmxResponse: Proteins
        """
        omx = omxware.omxware(self.connection().config().token(), env=self.connection().config().env())
        results = omx.proteins(go_terms=self.id(), page_size=page_size, page_number=page_number)

        return results

    def domains(self,
                page_size=Entity._PAGE_SIZE_DEFAULT,
                page_number=Entity._PAGE_INDEX_DEFAULT
                ):
        """
        Get OMXWare Domains for this GO Term

        Parameters:
            :param page_number: Page Number
            :type page_number: int

            :param page_size: Results page size
            :type page_size: int

        Returns:
            :return:    OmxResponse: Domains
        """
        omx = omxware.omxware(self.connection().config().token(), env=self.connection().config().env())
        results = omx.domains(go_terms=self.id(), page_size=page_size, page_number=page_number)

        return results

