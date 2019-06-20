# -*- coding: utf-8 -*-

from omxware import omxware
from omxware.config import Connection

from omxware.entities.Domain import Domain
from omxware.entities.Entity import Entity
from omxware.entities.Genome import Genome
from omxware.entities.Genus import Genus
from omxware.entities.GoTerm import Go
from omxware.entities.IprCode import Ipr

from omxware.utils.ResultUtils import list2str


class Protein(Entity):
    """OMXWare Protein Entity Class"""

    _sequence_length = None  # int
    _sequence = None  # str
    _genus = None  # [Genus]
    _genomes = None  # [Genome]
    _domains = None  # [Domain]
    _goterms = None  # [GoTerm]
    _iprcodes = None  # [IprCode]

    def __init__(self, connecthdr: Connection, protein):
        """
        Construction

        {id, name, type, json} attributes are read by the super().constructor()
        So just parse and load the remaining attributes
        """

        super().__init__(connecthdr, protein)

        if isinstance(protein, dict):
            if not ("id" in protein):
                raise Exception("The Protein id missing")

            # extracting the sequence_length
            if 'sequence_length' in protein:
                self._sequence_length = protein['sequence_length']

            # extracting the sequence
            if 'sequence' in protein:
                self._sequence = protein['sequence']
                self._is_preview_obj = False
            else:
                self._is_preview_obj = True

            # extracting the genomes for this Protein
            if 'genomes' not in protein:
                self._is_preview_obj = True
                self._genomes = None
            else:
                self._is_preview_obj = False

                self._genomes = []
                genome_lst = protein['genomes']

                if isinstance(genome_lst, list):
                    for genome in genome_lst:
                        genome_obj = Genome(self._connecthdr, genome)
                        self._genomes.append(genome_obj)

                elif isinstance(genome_lst, str):
                    genome_obj = Genome(self._connecthdr, genome_lst)
                    self._genomes.append(genome_obj)

            # extracting the genus for this Protein
            if 'genera' not in protein:
                self._genus = None
                self._is_preview_obj = True
            else:
                self._genus = []
                genus_lst = protein['genera']

                if isinstance(genus_lst, list):
                    for genus in genus_lst:
                        genus_obj = Genus(self._connecthdr, genus)
                        self._genus.append(genus_obj)

                elif isinstance(genus_lst, str):
                    genus_obj = Genus(self._connecthdr, genus_lst)
                    self._genus.append(genus_obj)

            # extracting the genus for this Protein
            if 'domains' not in protein:
                self._domains = None
            else:
                self._domains = []
                domains_lst = protein['domains']

                if isinstance(domains_lst, list):
                    for domain in domains_lst:
                        domain_obj = Domain(self._connecthdr, domain)
                        self._domains.append(domain_obj)

                elif isinstance(domains_lst, str):
                    domain_obj = Domain(self._connecthdr, domains_lst)
                    self._domains.append(domain_obj)

            # extracting the go_terms for this Protein
            if 'go_codes' not in protein:
                self._goterms = None
            else:
                self._goterms = []
                go_lst = protein['go_codes']

                if isinstance(go_lst, list):
                    self._goterms = []
                    for go in go_lst:
                        self._goterms.append(go)

                elif isinstance(go_lst, str):
                    self._goterms.append(go_lst)

            # extracting the ipr_codes for this Protein
            if 'interproscan_ids' not in protein:
                self._iprcodes = None
                print('Sorry no IPR codes for ' + self.type() + ': ' + self.id())
            else:
                self._iprcodes = []
                ipr_lst = protein['interproscan_ids']

                if isinstance(ipr_lst, list):
                    for ipr in ipr_lst:
                        self._iprcodes.append(ipr)

                elif isinstance(go_lst, str):
                    self._iprcodes.append(ipr_lst)

            self._json = protein

        elif isinstance(protein, str):
            self._is_preview_obj = True
            self._id = protein

        self._type = 'protein'

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
                p = Protein(self._connecthdr, result)
                self.__copy(p)
            else:
                raise Exception('Invalid OMXWare Protein ID')

    def __copy(self, protein):
        self._is_preview_obj = protein.is_preview_obj()
        self._connecthdr = protein.connection()
        self._config = protein.configuration()
        self._omx_token = protein.omx_token()

        self._json = protein.json()

        self._id = protein.id()
        self._type = protein.type()
        self._name = protein.name()

        self._sequence_length = protein.sequence_length()
        self._sequence = protein.sequence()
        self._genus = protein._genus
        self._genomes = protein._genomes
        self._domains = protein._domains
        self._goterms = protein._go
        self._iprcodes = protein._ipr

    def _2fasta(self):
        id = self.id()
        name = self.name()
        seq = self.sequence()
        typ = 'protein'

        fasta = '>OMX_' + typ + '_' + id + '|' + name + "\n" + seq

        return fasta

    def sequence(self):
        """
        Get this Protein's sequence

        Returns:
            :return: str :   Protein Sequence
        """
        if self._sequence is None and self.is_preview_obj():
            self.__reload()

        return self._sequence

    def sequence_length(self):
        """
        Get this Protein's sequence length

        Returns:
            :return: int :   Protein Sequence's length
        """
        if self._sequence_length is None and self.is_preview_obj():
            self.__reload()

        return int(self._sequence_length)

    def genus(self,
              page_size=Entity._PAGE_SIZE_DEFAULT,
              page_number=Entity._PAGE_INDEX_DEFAULT
              ):
        """
        Get all the associated Genera for this Protein

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

    def genomes(self,
                page_size=Entity._PAGE_SIZE_DEFAULT,
                page_number=Entity._PAGE_INDEX_DEFAULT
                ):
        """
        Get all the associated Genomes for this Protein

        Parameters:
            :param page_number: Page Number
            :type page_number: int

            :param page_size: Results page size
            :type page_size: int

        Returns:
            :return:    OmxResponse: Genomes
        """
        if self._genomes is None and self.is_preview_obj():
            self.__reload()

        if self._genomes is None and not self.is_preview_obj():
            return None

        genome_list = self._genomes
        offset = (page_number - 1) * page_size

        ids = []
        for genome in genome_list[offset:page_size]:
            ids.append(genome.id())

        if len(ids) == 0:
            return None

        omx = omxware.omxware(self.connection().config().token(), env=self.connection().config().env())
        results = omx.genomes(ids=ids, page_size=len(ids), page_number=page_number)
        return results

    # def genes(self):
    #     print('Get Genes for ' + self.type() + ': ' + self.id())

    def domains(self,
                page_size=Entity._PAGE_SIZE_DEFAULT,
                page_number=Entity._PAGE_INDEX_DEFAULT
                ):
        """
        Get all the associated Domains for this Protein

        Parameters:
            :param page_number: Page Number
            :type page_number: int

            :param page_size: Results page size
            :type page_size: int

        Returns:
            :return:    OmxResponse: Domains
        """
        if self._domains is None and self.is_preview_obj():
            self.__reload()

        if self._domains is None and not self.is_preview_obj():
            return None

        domain_list = self._domains
        offset = (page_number - 1) * page_size

        ids = []
        for domain in domain_list[offset:page_size]:
            ids.append(domain.id())

        if len(ids) == 0:
            return None

        omx = omxware.omxware(self.connection().config().token(), env=self.connection().config().env())
        results = omx.domains(ids=ids, page_size=len(ids), page_number=page_number)
        return results

    def go(self,
           page_size=Entity._PAGE_SIZE_DEFAULT,
           page_number=Entity._PAGE_INDEX_DEFAULT
           ):
        """
        Get all the associated GO terms for this Protein

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
        Get all the associated GO terms for this Protein

        Parameters:
            :param page_number: Page Number
            :type page_number: int

            :param page_size: Results page size
            :type page_size: int

        Returns:
            :return: OmxResponse:   Ipr
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
