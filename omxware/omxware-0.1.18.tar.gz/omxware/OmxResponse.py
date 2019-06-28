# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import random
from requests import Response

from omxware.entities.Domain import Domain
from omxware.entities.Gene import Gene
from omxware.entities.Genome import Genome
from omxware.entities.Genus import Genus
from omxware.entities.GoTerm import Go
from omxware.entities.IprCode import Ipr
from omxware.entities.Protein import Protein
from omxware.entities.User import User


class OmxResponse:
    __connect_hdr = None
    __results = None  # []
    __results_json = None  # []
    __facets = None  # {}
    __page_size = -1
    __page_number = -1
    __total_results = -1
    __message = None
    __response_time = -1
    __http_response_code = -1
    __error = None

    __results_type = None

    def __init__(self, connecthdr, omx_response: Response):
        self.__connect_hdr = connecthdr

        if isinstance(omx_response, Response):

            if omx_response is not None:
                js0n = omx_response.json()

                self.__http_response_code = omx_response.status_code
                self.__page_size = int(js0n['page_size'])
                self.__page_number = int(js0n['page_index'])
                self.__total_results = int(js0n['total_results'])
                self.__response_time = js0n['time_taken']
                self.__message = js0n['message']

                if ('results' in js0n) and (self.__total_results > 0) and len(js0n["results"]) > 0:
                    self.__process_results(js0n["results"])
                    self.__results_json = js0n["results"]
                else:
                    self.__results = []

                if ('facets' in js0n) and len(js0n["facets"]) > 0:
                    self.__process_facets(js0n["facets"])
                else:
                    self.__facets = {}

            else:
                return None

    def type(self):
        """
        Get Response type

        Returns:
            :returns:   str:    Response type
        """
        return self.__results_type

    def page_size(self):
        """
        Get Response page size

        Returns:
            :returns:   str:    Response page size
        """
        return self.__page_size

    def page_index(self):
        """
        Get Response page number

        Returns:
            :returns:   str:    Response page number
        """
        return self.__page_number

    def total_results(self):
        """
        Get total number of results for the query

        Returns:
            :returns:   int:    Total number of results
        """
        return self.__total_results

    def response_time(self):
        """
        Get Response time for the query

        Returns:
            :returns:   str:    Response time
        """
        return self.__response_time

    def message(self):
        """
        OMXWare response comment

        Returns:
            :returns:   str:    Message
        """
        return self.__message

    def error(self):
        """
        OMXWare Query errors / exceptions

        Returns:
            :returns:   str:    Error messages
        """
        return self.__error

    def results(self, type='list'):
        """
            Get the results for in the chosen output format

            Parameters:
                type (str): one of {'list', 'json', 'df', 'fasta'}

            Returns:
                'list'      => OMXWare query results as list
                'json'      => List of OMXWare query results as a json array
                'df'        => List of OMXWare query results as a Pandas data-frame
                'fasta'     => (Only for Genes and/or Proteins) Get results as Fasta
        """

        if type == 'list':
            return self.__results

        elif type == 'df':
            df = pd.DataFrame(self.__2json(self.__results))
            return df

        elif type == 'json':
            return self.__2json(self.__results)

        elif type == 'fasta':
            return self.__2fasta(self.__results)

    def facets(self):
        return self.__facets

    def __process_results(self, results):
        results_tmp = []

        if isinstance(results, list):
            for result in results:

                typ = None

                if 'type' in result:
                    typ = result['type']
                    self.__results_type = typ

                if typ is not None:
                    if typ == 'genus':
                        genus_obj = Genus(self.__connect_hdr, result)
                        results_tmp.append(genus_obj)

                    elif typ == 'genome':
                        genome_obj = Genome(self.__connect_hdr, result)
                        results_tmp.append(genome_obj)

                    elif typ == 'gene':
                        gene_obj = Gene(self.__connect_hdr, result)
                        results_tmp.append(gene_obj)

                    elif typ == 'protein':
                        protein_obj = Protein(self.__connect_hdr, result)
                        results_tmp.append(protein_obj)

                    elif typ == 'domain':
                        domain_obj = Domain(self.__connect_hdr, result)
                        results_tmp.append(domain_obj)

                    elif typ == 'go':
                        go_obj = Go(self.__connect_hdr, result)
                        results_tmp.append(go_obj)

                    elif typ == 'ipr':
                        ipr_obj = Ipr(self.__connect_hdr, result)
                        results_tmp.append(ipr_obj)

                    elif typ == 'user':
                        user_obj = User(self.__connect_hdr, result)
                        results_tmp.append(user_obj)
                else:
                        results_tmp.append(result)
                        self.__results_type = 'Unknown'

            self.__results = results_tmp

    def __process_facets(self, facets):
        facets_tmp = {}

        if facets is not None and isinstance(facets, dict):
            for facet_key in facets.keys():
                facet = facets.get(facet_key)
                tmp_list = []

                for facet_by_key in facet:
                    name = facet_by_key.get('type')
                    count = facet_by_key.get('count')

                    tmp_list.append({'name': name, 'count': count})

                facets_tmp[facet_key.replace('.keyword', '')] = tmp_list

        self.__facets = facets_tmp

    @staticmethod
    def __2json(res_list):
        result = []
        for res in res_list:
            if not isinstance(res, dict):
                res = res.json()
                try:
                    del res['sequence']
                except KeyError:
                    pass

            result.append(res)

        return result

    def __2fasta(self, res_list):
        if self.type() in ['gene', 'protein']:
            fasta = ''

            for res in res_list:
                res = res._2fasta()

                if len(fasta) > 0:
                    fasta = fasta + "\n"

                fasta = fasta + res

            return fasta

        else:
            raise Exception("'Fasta' output format only for Genes / Proteins")


    def __str__(self):
        res_str = str(self.__results_json)
        fac_str = str(self.__facets)

        if len(res_str) > 75:
            res_str = res_str[0:75] + "... "

        if len(fac_str) > 75:
            fac_str = fac_str[0:75] + "... "

        string = "\n---------------------------------------------------------------------------------------------------" + \
                 "\nPage: \t\t\t" + str(self.__page_number) + " " + \
                 "\nPage Size: \t\t" + str(self.__page_size) + " " + \
                 "\nTotal Results: \t" + str(self.__total_results) + " " + \
                 "\nResults: \t\t" + res_str + " " + \
                 "\nFacets: \t\t" + fac_str + " " + \
                 "\nMessage: \t\t" + self.__message + " " + \
                 "\n---------------------------------------------------------------------------------------------------" + \
                 "\n use .results() to get the results " +   \
                 "\n---------------------------------------------------------------------------------------------------"

        return string

    def show_facets(self, name='type', topN=5):
        if self.facets() is not None and name in self.facets():

            rand = random.randint(1, topN-1)
            explode = [0] * topN
            explode[rand] = 0.15

            distribution = self.facets()[name]
            df = (pd.DataFrame(distribution).sort_values(by='count', ascending=False))[:topN]
            plt.pie(
                # using data total)arrests
                df['count'],
                # with the labels being officer names
                labels=df['name'],
                # with no shadows
                shadow=False,
                # with colors
                # colors=colors,
                # with one slide exploded out
                explode=explode,
                # with the start angle at 90%
                startangle=90,
                # with the percent listed as a fraction
                autopct='%1.1f%%',
            )

            # View the plot drop above
            plt.axis('equal')
            plt.rcParams['figure.figsize'] = [90, 90]
            plt.rcParams['figure.dpi'] = 80

            # View the plot
            plt.tight_layout()
            plt.show()
