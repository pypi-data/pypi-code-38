from omxware import omxware

from omxware.config import Connection
from omxware.entities.Entity import Entity
from omxware.entities.Genus import Genus
from omxware.utils.ResultUtils import list2str


class Genome(Entity):
    """OMXWare Genome Entity Class"""

    _genus = None  # []
    _genome_type = None  # str
    _taxid = None  # str
    _metadata = None  # {}

    _supported_metadata_types = ['biosample']

    def __init__(self, connecthdr: Connection, genome):
        """Constructor"""

        """
        {id, name, type, json} attributes are read by the super().constructor()
        So just parse and load the remaining attributes
        """
        super().__init__(connecthdr, genome)

        if isinstance(genome, dict):
            if self._metadata is None:
                #   This Genome does not have any metadata
                self._metadata = {}

                # loading the metadata
                if 'metadata' in genome:
                    for metadata_type in self._supported_metadata_types:
                        if metadata_type in genome['metadata']:
                            self._metadata[metadata_type] = genome['metadata'][metadata_type]

            self._json = genome

            if 'genome_type' in genome:
                self._genome_type = genome['genome_type']

            if 'taxid' in genome:
                self._taxid = genome['taxid']

            # extracting the genus for this genome
            if 'genera' not in genome:
                self._is_preview_obj = True
            else:
                self._is_preview_obj = False
                self._genus = []
                genus_lst = genome['genera']

                if isinstance(genus_lst, list):
                    for genus in genus_lst:
                        genus_obj = Genus(self._connecthdr, genus)
                        self._genus.append(genus_obj)

                elif isinstance(genus_lst, str):
                    genus_obj = Genus(self._connecthdr, genus_lst)
                    self._genus.append(genus_obj)

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
                g = Genome(self._connecthdr, result.json())
                self.__copy(g)

    def __copy(self, genome):
        self._is_preview_obj = genome.is_preview_obj()
        self._connecthdr = genome.connection()
        self._config = genome.configuration()
        self._omx_token = genome.omx_token()

        self._json = genome.json()

        self._id = genome.id()
        self._type = genome.type()
        self._name = genome.name()

        self._genus = genome._genus
        self._metadata = genome.metadata()

        self._genome_type = genome.genome_type()
        self._taxid = genome.taxid()

    def taxid(self):
        """
        Get this Genome's Tax ID

        Returns:
            :return: str :   Tax ID
        """
        return self._taxid

    def genome_type(self):
        """
        Get this Genome's type. Will be one of { 'REFSEQ’, 'SRA’, ‘GENBANK’ }

        Returns:
            :return: str :   Genome type
        """
        if self._genome_type is None:
            return 'None'

        return self._genome_type

    def metadata(self, type='biosample'):
        """
        Get Genome metadata

        Parameters:
            :param type: Genome metadata. Must be one of ['biosample']
            :type type: str

        Returns:
            OmxResponse: Genome Metadata
            :return:    dict: Genome metadata
        """

        if type.lower() in (name.lower() for name in self._supported_metadata_types):
            # making sure the metadata type requested is one of the type we support
            if self._metadata is not None:
                if type in self._metadata:
                    # checking if we loaded the metadata for this genome
                    return self._metadata[type]
            elif self.is_preview_obj():
                self._reload()
                return self.metadata(type)

            return None

    def file(self, output_file_path=None):
        """
        Get Genome Assembly file

        Parameters:
            :param output_file_path: File path to Download the Assembly file
            :type output_file_path: str

        Returns:
            :return:    str:
                File path ( if output_file_path is not None )
                Assembly file as String
        """

        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/octet-stream'}
        params = {}

        methodurl = '/api/public/genomes/id:' + self.id() +'/file'

        resp = self.connection().get_file(methodurl=methodurl, headers=headers, payload=params)

        if output_file_path is not None:
            try:
                f = open(output_file_path, "w+")
                f.write(resp)
                f.close()

                return output_file_path
            except:
                print("Could not write to output file!!")
                return

        else:
            return resp

    def genus(self,
              page_size=Entity._PAGE_SIZE_DEFAULT,
              page_number=Entity._PAGE_INDEX_DEFAULT
              ):
        """
        Get OMXWare Genera the Genome

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
        offset = (page_number-1) * page_size

        ids = []
        for genus in genus_list[offset:page_size]:
            ids.append(genus.name())

        if len(ids) == 0:
            return None

        omx = omxware.omxware(self.connection().config().token(), env=self.connection().config().env())
        results = omx.genus(genus_names=ids, page_size=len(ids), page_number=page_number)
        return results

    def genes(self,
              page_size=Entity._PAGE_SIZE_DEFAULT,
              page_number=Entity._PAGE_INDEX_DEFAULT
              ):
        """
        Get OMXWare Genes for the Genome

        Parameters:
            :param page_number: Page Number
            :type page_number: int

            :param page_size: Results page size
            :type page_size: int

        Returns:
            :return:    OmxResponse: Genes
        """
        omx = omxware.omxware(self.connection().config().token(), env=self.connection().config().env())
        results = omx.genes(genome_ids=self.id(), page_size=page_size, page_number=page_number)

        return results

    def proteins(self,
                 page_size=Entity._PAGE_SIZE_DEFAULT,
                 page_number=Entity._PAGE_INDEX_DEFAULT
                 ):
        """
        Get OMXWare Proteins for the Genome

        Parameters:
            :param page_number: Page Number
            :type page_number: int

            :param page_size: Results page size
            :type page_size: int

        Returns:
            :return:    OmxResponse: Proteins
        """
        omx = omxware.omxware(self.connection().config().token(), env=self.connection().config().env())
        results = omx.proteins(genome_ids=self.id(), page_size=page_size, page_number=page_number)

        return results


