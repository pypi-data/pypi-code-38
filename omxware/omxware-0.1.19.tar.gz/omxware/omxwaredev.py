# -*- coding: utf-8 -*-

"""
OMXWare SDK
"""

import sys
from datetime import datetime, timedelta

from omxware import omxware, list2str
from omxware.exceptions.InvalidParamsException import InvalidParamsError
from omxware.utils.AESCipher import AESCipher
from omxware.utils.SecUtils import rand

token = ''


def get_token(username, password):
    """
    Verify the credentials and get a User Token

    Parameters:
            :param username: OMXWare username. This is different from your IBM Id username
            :type username: str

            :param password: OMXWare password. This is different from your IBM Id's password
            :type password: str

    Returns:
        OMXWare user token

    Raises:
        KeyError: Raises an exception.
    """

    if username is None:
        sys.exit("Username cannot be empty!")

    if password is None:
        sys.exit("Password cannot be empty!")

    # Verify username and password

    cipher = AESCipher()
    omxware_token = cipher.encrypt(rand() + "::::" + username + "::::" + password)

    return omxware_token


class OmxwareDev(omxware):
    PAGE_SIZE_DEFAULT = 25
    PAGE_INDEX_DEFAULT = 1

    def __init__(self, omxware_token, env='master'):
        """
        Initialize an OMXWare session.

        Parameters:
            :param omxware_token: OMXWare Token. use
            :type omxware_token: str

            :param env: OMXWare `env` type. Must be one of ['master', 'dev', 'dev_search', 'local']
            :type env: str
        """

        super().__init__(omxware_token, env)

# User
    def whoami(self):
        """
        Get OMXWare User info .

        Returns:
            :return:    OmxResponse :   User
        """
        try:

            self._init_omx_connection()
            methodurl = "/api/secure/user/profile"

            headers = {'content-type': 'application/json',
                       'content-language': 'en-US',
                       'accept': 'application/json'}

            params = {}

            resp = self.connection.get(methodurl=methodurl, headers=headers, payload=params)
            return resp
        except InvalidParamsError as ex:
            print("\nERROR: " + str(ex))
            help(self.whoami)

# OMXWare Registrations / Login Metrics
    def events(self, type=None, lastNdays=30, page_size=50000, page_nummber=1):
        """
        Get OMXWare User Events

        Parameters:
            :param: type:   str:    Must be one of { 'login', 'register' }
            :param: lastNdays:  int:    last N days to query the events


        Returns:
            :return:    OmxResponse :   User
        """
        try:
            today = datetime.today().strftime('%Y-%m-%d')
            date_N_days_ago = (datetime.today() - timedelta(days=lastNdays)).strftime('%Y-%m-%d')

            if type is not None:
                self._init_omx_connection()
                methodurl = '/api/secure/admin/omx-user-stats/from/' + date_N_days_ago + '/to/' + today + '/size/' + str(page_size) + '/page/' + str(page_nummber) + '?event_type='+type

                headers = {'content-type': 'application/json',
                           'content-language': 'en-US',
                           'accept': 'application/json'}

                params = {}

                resp = self.connection.get(methodurl=methodurl, headers=headers, payload=params)
                return resp

            else:
                return None
        except InvalidParamsError as ex:
            print("\nERROR: " + str(ex))
            help(self.events)
            return None

        #  Genomes
    def genomes(self,
                ids=None,
                genus_names=None,
                genome_type=None,
                genome_taxid=None,
                resistant_only=False,
                created_before=None,
                created_after=None,
                modified_before=None,
                modified_after=None,
                page_size=PAGE_SIZE_DEFAULT,
                page_number=PAGE_INDEX_DEFAULT
                ):
        """
        Get OMXWare Genomes by List of Genome ID(s) and/or Genus name(s) .

        Parameters:
            :param ids: List of Genome IDs
            :type ids: [str]

            :param genus_names: List of Genus names
            :type genus_names: [str]

            :param genus_names: List of Genome Types. Must be one of { 'REFSEQ’, 'SRA’, ‘GENBANK’ }
            :type genus_names: [str]

            :param genus_names: List of Genome Tax ids
            :type genus_names: [str]

            :param created_before: Date - Created / Imported before. Must be in YYYY-MM-DD format. Can also be YYYY-MM or Just YYYY
            :type created_before: [str]

            :param created_after: Date - Created / Imported after. Must be in YYYY-MM-DD format. Can also be YYYY-MM or Just YYYY
            :type created_after: [str]

            :param modified_before: Date - Modified before. Must be in YYYY-MM-DD format. Can also be YYYY-MM or Just YYYY
            :type modified_before: [str]

            :param modified_after: Date - Modified after. Must be in YYYY-MM-DD format. Can also be YYYY-MM or Just YYYY
            :type modified_after: [str]

            :param page_number: Page Number
            :type page_number: int

            :param page_size: Results page size
            :type page_size: int

        Returns:
            :return:    OmxResponse: Genome
        """
        try:

            self._init_omx_connection()
            headers = {'content-type': 'application/json',
                       'content-language': 'en-US',
                       'accept': 'application/json'}
            params = {'page_size': page_size, 'page_number': page_number}

            if ids is not None:
                methodurl = "/api/public/genomes/id:"

                if isinstance(ids, list):
                    methodurl = methodurl + list2str(ids)

                if isinstance(ids, str):
                    methodurl = methodurl + ids

                resp = self.connection.get(methodurl=methodurl, headers=headers, payload=params)
                return resp

            methodurl = "/api/public/genomes/"

            if isinstance(genus_names, list):
                params['name'] = list2str(genus_names)

            if isinstance(genus_names, str):
                params['name'] = [genus_names]

            if isinstance(genome_type, list):
                params['type'] = list2str(genome_type)

            if isinstance(genome_type, str):
                params['type'] = [genome_type]

            if isinstance(genome_taxid, list):
                params['taxid'] = list2str(genome_taxid)

            if isinstance(genome_taxid, str) or isinstance(genome_taxid, int):
                params['taxid'] = [genome_taxid]

            if resistant_only:
                params['resistant_only'] = 'true'
            else:
                params['resistant_only'] = 'false'

            created = []
            modified = []

            if created_before is not None and isinstance(created_before, str):
                created.append('lte:' + created_before)

            if created_after is not None and isinstance(created_after, str):
                created.append('gte:' + created_after)

            if len(created) > 0:
                params['created'] = created

            if modified_before is not None and isinstance(modified_before, str):
                modified.append('lte:' + modified_before)

            if modified_after is not None and isinstance(modified_after, str):
                modified.append('gte:' + modified_after)

            if len(modified) > 0:
                params['modified'] = modified

            resp = self.connection.get(methodurl=methodurl, headers=headers, payload=params)
            return resp
        except InvalidParamsError as ex:
            print("\nERROR: " + str(ex))
            help(self.genomes)

    #  Genes
    def genes(self,
              ids=None,
              sequence=None,
              gene_name=None,
              genome_ids=None,
              genus_names=None,
              go_terms=None,
              ipr_ids=None,
              resistant_only=False,
              sequence_length=None,
              page_size=PAGE_SIZE_DEFAULT,
              page_number=PAGE_INDEX_DEFAULT
              ):
        """
        Get OMXWare Genes.

        Parameters:
            :param ids: List of gene ids
            :type ids: [str]

            :param sequence: Gene sequence
            :type sequence: str

            :param gene_name:
            :type gene_name: str

            :param genome_ids: List of Genome IDs
            :type genome_ids: [str]

            :param genus_names: List of Genus names
            :type genus_names: [str]

            :param go_terms:
            :type go_terms: [str]

            :param ipr_ids:
            :type ipr_ids: [str]

            :param sequence_length:
            :type sequence_length: str

            :param page_number: (int): Page Number
            :type page_number: int

            :param page_size: (int): Results page size
            :type page_size: int

        Returns:
            :return:    OmxResponse: Gene
        """
        try:

            self._init_omx_connection()
            headers = {'content-type': 'application/json',
                       'content-language': 'en-US',
                       'accept': 'application/json'}
            params = {'page_size': page_size, 'page_number': page_number}

            if ids is not None:
                methodurl = "/api/public/genes/id:"

                if isinstance(ids, list):
                    methodurl = methodurl + list2str(ids)

                if isinstance(ids, str):
                    methodurl = methodurl + ids

                resp = self.connection.get(methodurl=methodurl, headers=headers, payload=params)
                return resp

            if sequence is not None:
                methodurl = "/api/public/genes/sequence:"

                if isinstance(sequence, str):
                    methodurl = methodurl + sequence

                resp = self.connection.get(methodurl=methodurl, headers=headers, payload=params)
                return resp

            methodurl = "/api/public/genes/"

            if isinstance(gene_name, str):
                params['gene_name'] = [gene_name]

            if isinstance(genome_ids, list):
                params['genome_id'] = list2str(genome_ids)

            if isinstance(genome_ids, str):
                params['genome_id'] = [genome_ids]

            if isinstance(genus_names, list):
                params['genus_name'] = list2str(genus_names)

            if isinstance(genus_names, str):
                params['genus_name'] = [genus_names]

            if isinstance(go_terms, list):
                params['go_term'] = list2str(go_terms)

            if isinstance(go_terms, str):
                params['go_term'] = [go_terms]

            if isinstance(ipr_ids, list):
                params['ipr_id'] = list2str(ipr_ids)

            if isinstance(ipr_ids, str):
                params['ipr_id'] = [ipr_ids]

            if isinstance(sequence_length, str):
                params['sequence_length'] = [sequence_length]

            if resistant_only:
                params['resistant_only'] = 'true'
            else:
                params['resistant_only'] = 'false'

            resp = self.connection.get(methodurl=methodurl, headers=headers, payload=params)
            return resp

        except InvalidParamsError as ex:
            print("\nERROR: " + str(ex))
            help(self.genes)

# OMXWare Jobs for current user
#     def jobs(self, type=None, lastNdays=30, page_size=50000, page_nummber=1):
#         """
#         Get OMXWare User Events
#
#         Parameters:
#             :param: type:   str:    Must be one of { 'login', 'register' }
#             :param: lastNdays:  int:    last N days to query the events
#
#
#         Returns:
#             :return:    OmxResponse :   User
#         """
#         try:
#             today = datetime.today().strftime('%Y-%m-%d')
#             date_N_days_ago = (datetime.today() - timedelta(days=lastNdays)).strftime('%Y-%m-%d')
#
#             if type is not None:
#                 self._init_omx_connection()
#                 methodurl = '/api/secure/admin/omx-user-stats/from/' + date_N_days_ago + '/to/' + today + '/size/' + str(page_size) + '/page/' + str(page_nummber) + '?event_type='+type
#
#                 headers = {'content-type': 'application/json',
#                            'content-language': 'en-US',
#                            'accept': 'application/json'}
#
#                 params = {}
#
#                 resp = self.connection.get(methodurl=methodurl, headers=headers, payload=params)
#                 return resp
#
#             else:
#                 return None
#         except InvalidParamsError as ex:
#             print("\nERROR: " + str(ex))
#             help(self.events)
#             return None
