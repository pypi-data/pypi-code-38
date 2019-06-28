# -*- coding: utf-8 -*-

from omxware import omxware
from omxware.config import Connection

from omxware.entities.Entity import Entity as Entity
from omxware.entities.Genus import Genus
from omxware.entities.GoTerm import Go
from omxware.entities.IprCode import Ipr

from omxware.utils.ResultUtils import list2str


class Domain(Entity):
    """OMXWare Domain Entity Class"""

    _sequence_length = None  # int
    _sequence = None  # str
    _genus = None  # [Genus]
    _proteins = None  # [Protein]
    _goterms = None  # [GoTerm]
    _iprcodes = None  # [IprCode]

    def __init__(self, connecthdr: Connection, domain):
        """
        Construction

        {id, name, type, json} attributes are read by the super().constructor()
        So just parse and load the remaining attributes
        """
        super().__init__(connecthdr, domain)

        if isinstance(domain, dict):
            if not ("id" in domain):
                raise Exception("The Domain id missing")

            # extracting the sequence_length
            if 'sequence_length' in domain:
                self._sequence_length = domain['sequence_length']

            # extracting the sequence
            if 'sequence' in domain:
                self._sequence_length = domain['sequence']
                self._is_preview_obj = False
            else:
                self._is_preview_obj = True

            # extracting the genus for this Domain
            if 'genera' not in domain:
                self._genus = None
                self._is_preview_obj = True
            else:
                self._genus = []
                genus_lst = domain['genera']

                if isinstance(genus_lst, list):
                    for genus in genus_lst:
                        genus_obj = Genus(self._connecthdr, genus)
                        self._genus.append(genus_obj)

                elif isinstance(genus_lst, str):
                    genus_obj = Genus(self._connecthdr, genus_lst)
                    self._genus.append(genus_obj)

            # extracting the proteins for this Domain
            if 'proteins' not in domain:
                self._proteins = None
                self._is_preview_obj = True
            else:
                self._proteins = []
                proteins_lst = domain['proteins']

                from omxware.entities.Protein import Protein

                if isinstance(proteins_lst, list):
                    for protein in proteins_lst:
                        protein_obj = Protein(self._connecthdr, protein)
                        self._proteins.append(protein_obj)

                elif isinstance(proteins_lst, str):
                    protein_obj = Protein(self._connecthdr, proteins_lst)
                    self._proteins.append(protein_obj)

            # extracting the go_terms for this Domain
            if 'go_codes' not in domain:
                self._goterms = None
            else:
                self._goterms = []
                go_lst = domain['go_codes']

                if isinstance(go_lst, list):
                    for go in go_lst:
                        self._goterms.append(go)

                elif isinstance(go_lst, str):
                    self._goterms.append(go_lst)

            # extracting the ipr_codes for this Domain
            if 'interproscan_ids' not in domain:
                self._iprcodes = None
            else:
                self._iprcodes = []
                ipr_lst = domain['interproscan_ids']

                if isinstance(ipr_lst, list):
                    for ipr in ipr_lst:
                        self._iprcodes.append(ipr)

                elif isinstance(go_lst, str):
                    self._iprcodes.append(ipr_lst)

            self._json = domain

        elif isinstance(domain, str):
            self._is_preview_obj = True
            self._id = domain

        self._type = 'domain'

    def __reload(self):
        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        params = {'page_size': 1, 'page_number': 1}

        if self.id() is not None:
            methodurl = '/api/public/' + self.type() + 's/id:'

            if isinstance(self.id(), list):
                methodurl = methodurl + list2str(self.id())

            if isinstance(self.id(), str):
                methodurl = methodurl + self.id()

            resp = self._connecthdr.get(methodurl=methodurl, headers=headers, payload=params)
            results = resp.results()

            if results is not None:
                result = results[0]
                d = Domain(self._connecthdr, result)
                self.__copy(d)
            else:
                raise Exception('Invalid OMXWare Domain ID')

    def __copy(self, domain):
        self._is_preview_obj = domain.is_preview_obj()
        self._connecthdr = domain.connection()
        self._config = domain.configuration()
        self._omx_token = domain.omx_token()

        self._json = domain.json()

        self._id = domain.id()
        self._type = domain.type()
        self._name = domain.name()

        self._sequence_length = domain.sequence_length()
        self._sequence = domain.sequence()
        self._genus = domain._genus
        self._proteins = domain._proteins
        self._domains = domain._domains
        self._goterms = domain._go
        self._iprcodes = domain._ipr

    def sequence(self):
        """
        Get this Domain's sequence

        Returns:
            :return: str :   Domain Sequence
        """
        if self._sequence is None and self.is_preview_obj():
            self.__reload()

        return self._sequence

    def sequence_length(self):
        """
        Get this Domain's sequence length

        Returns:
            :return: int :   Domain Sequence's length
        """
        if self._sequence_length is None and self.is_preview_obj():
            self.__reload()

        return int(self._sequence_length)

    def genus(self,
              page_size=Entity._PAGE_SIZE_DEFAULT,
              page_number=Entity._PAGE_INDEX_DEFAULT
              ):
        """
        Get all the associated Genera for this Domain

        Parameters:
            :param page_number: Page Number
            :type page_number: int

            :param page_size: Results page size
            :type page_size: int

        Returns:
            :return:    OmxResponse: Genus
        """
        if self._genus is None and self.is_preview_obj():
            self.__reload()

        if self._genus is None and not self.is_preview_obj():
            return None

        genus_list = self._genus
        offset = (page_number - 1) * page_size

        ids = []
        for genus in genus_list[offset:page_size]:
            ids.append(genus.name())

        if len(ids) == 0:
            return None

        omx = omxware.omxware(self.connection().config().token(), env=self.connection().config().env())
        results = omx.genus(genus_names=ids, page_size=len(ids), page_number=page_number)
        return results

    def proteins(self,
                page_size=Entity._PAGE_SIZE_DEFAULT,
                page_number=Entity._PAGE_INDEX_DEFAULT
                ):
        """
        Get all the associated Genomes for this Domain

        Parameters:
            :param page_number: Page Number
            :type page_number: int

            :param page_size: Results page size
            :type page_size: int

        Returns:
            :return:    OmxResponse: Proteins
        """
        if self._proteins is None and self.is_preview_obj():
            self.__reload()

        if self._proteins is None and not self.is_preview_obj():
            return None

        protein_list = self._proteins
        offset = (page_number - 1) * page_size

        ids = []
        for protein in protein_list[offset:page_size]:
            ids.append(protein.id())

        if len(ids) == 0:
            return None

        omx = omxware.omxware(self.connection().config().token(), env=self.connection().config().env())
        results = omx.proteins(ids=ids, page_size=len(ids), page_number=page_number)
        return results

    # def genes(self):
    #     print('Get Proteins for ' + self.type() + ': ' + self.id())

    def go(self,
           page_size=Entity._PAGE_SIZE_DEFAULT,
           page_number=Entity._PAGE_INDEX_DEFAULT
           ):
        """
        Get all the associated GO terms for this Domain

        Parameters:
            :param page_number: Page Number
            :type page_number: int

            :param page_size: Results page size
            :type page_size: int

        Returns:
            :return:    OmxResponse: GO
        """
        if self._goterms is None and self.is_preview_obj():
            self.__reload()

        if self._goterms is None and not self.is_preview_obj():
            return None

        go_list = self._goterms
        offset = (page_number - 1) * page_size

        ids = []
        for go in go_list[offset:page_size]:
            if isinstance(go, Go):
                ids.append(go.id())
            elif isinstance(go, str):
                ids.append(go)

        if len(ids) == 0:
            return None

        omx = omxware.omxware(self.connection().config().token(), env=self.connection().config().env())
        results = omx.go(ids=ids, page_size=len(ids), page_number=page_number)
        return results

    def ipr(self,
            page_size=Entity._PAGE_SIZE_DEFAULT,
            page_number=Entity._PAGE_INDEX_DEFAULT
            ):
        """
        Get all the associated GO terms for this Domain

        Parameters:
            :param page_number: Page Number
            :type page_number: int

            :param page_size: Results page size
            :type page_size: int

        Returns:
            :return:    OmxResponse: Iprs
        """
        if self._iprcodes is None and self.is_preview_obj():
            self.__reload()

        if self._iprcodes is None and not self.is_preview_obj():
            return None

        ipr_list = self._iprcodes
        offset = (page_number - 1) * page_size

        ids = []
        for ipr in ipr_list[offset:page_size]:
            if isinstance(ipr, Ipr):
                ids.append(ipr.id())
            elif isinstance(ipr, str):
                ids.append(ipr)

        if len(ids) == 0:
            return None

        omx = omxware.omxware(self.connection().config().token(), env=self.connection().config().env())
        results = omx.ipr(ids=ids, page_size=len(ids), page_number=page_number)
        return results
