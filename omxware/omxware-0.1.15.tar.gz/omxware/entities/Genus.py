# -*- coding: utf-8 -*-

from omxware import omxware

from omxware.config import Connection
from omxware.entities.Entity import Entity


class Genus(Entity):
    """OMXWare Genus Entity Class"""

    def __init__(self, connecthdr: Connection, genus):
        super().__init__(connecthdr, genus)

        """Constructor"""
        if genus is None:
            raise Exception('Invalid Genus Object initialization. None value passed')

        if isinstance(genus, dict):
            if not ("name" in genus):
                raise Exception("The Genus name missing")

            self._name = genus['name']
            self._id = genus['id']

            self._is_preview_obj = False
            self._json = genus

        elif isinstance(genus, str):
            self._id = genus
            self._name = genus
            self._is_preview_obj = False # this doesn't matter for Genus objects

        self._type = 'genus'

    def __reload(self):
        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        params = {'page_size': 1, 'page_number': 1}

        if self.id() is not None:
            methodurl = '/api/public/genus/'

            id = self.id()
            params['name'] = id

            resp = self._connecthdr.get(methodurl=methodurl, headers=headers, payload=params)
            results = resp.results()

            if results is not None:
                result = results[0]
                self = Genus(self._connecthdr, result)

    def genomes(self,
                page_size=Entity._PAGE_SIZE_DEFAULT,
                page_number=Entity._PAGE_INDEX_DEFAULT
                ):
        """
        Get OMXWare Genomes for the Genus

        Parameters:
            :param page_number: Page Number
            :type page_number: int

            :param page_size: Results page size
            :type page_size: int

        Returns:
            :return:    OmxResponse: Genomes
        """
        omx = omxware.omxware(self.connection().config().token(), env=self.connection().config().env())
        results = omx.genomes(genus_names=self.id(), page_size=page_size, page_number=page_number)

        return results

    def genes(self,
              page_size=Entity._PAGE_SIZE_DEFAULT,
              page_number=Entity._PAGE_INDEX_DEFAULT
              ):
        """
        Get OMXWare Genes for the Genus

        Parameters:
            :param page_number: Page Number
            :type page_number: int

            :param page_size: Results page size
            :type page_size: int

        Returns:
            :return:    OmxResponse: Genes
        """
        omx = omxware.omxware(self.connection().config().token(), env=self.connection().config().env())
        results = omx.genes(genus_names=self.id(), page_size=page_size, page_number=page_number)

        return results

    def proteins(self,
                 page_size=Entity._PAGE_SIZE_DEFAULT,
                 page_number=Entity._PAGE_INDEX_DEFAULT
                 ):
        """
        Get OMXWare Proteins for the Genus

        Parameters:
            :param page_number: Page Number
            :type page_number: int

            :param page_size: Results page size
            :type page_size: int

        Returns:
            :return:    OmxResponse: Proteins
        """
        omx = omxware.omxware(self.connection().config().token(), env=self.connection().config().env())
        results = omx.proteins(genus_names=self.id(), page_size=page_size, page_number=page_number)

        return results

    def domains(self,
                page_size=Entity._PAGE_SIZE_DEFAULT,
                page_number=Entity._PAGE_INDEX_DEFAULT
                ):
        """
        Get OMXWare Domains for the Genus

        Parameters:
            :param page_number: Page Number
            :type page_number: int

            :param page_size: Results page size
            :type page_size: int


        Returns:
            :return:    OmxResponse: Domains
        """
        omx = omxware.omxware(self.connection().config().token(), env=self.connection().config().env())
        results = omx.domains(genus_names=self.id(), page_size=page_size, page_number=page_number)

        return results
