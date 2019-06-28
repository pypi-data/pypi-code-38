#! /usr/bin/env python

import os
import argparse
import sys
import copy
import random
import requests
import logging
import csv
import json
import re
from datetime import datetime

import pandas as pd
from logging import config
import networkx

import ndex2
from ndex2.client import Ndex2
import ndexutil.tsv.tsv2nicecx2 as t2n
from ndexutil.config import NDExUtilConfig
from ndexutil.tsv.loaderutils import NetworkIssueReport
from ndexutil.tsv.loaderutils import NetworkUpdator
from ndexutil.tsv.loaderutils import GeneSymbolSearcher

import ndexsignorloader

logger = logging.getLogger(__name__)

TSV2NICECXMODULE = 'ndexutil.tsv.tsv2nicecx2'

LOG_FORMAT = "%(asctime)-15s %(levelname)s %(relativeCreated)dms " \
             "%(filename)s::%(funcName)s():%(lineno)d %(message)s"


LOAD_PLAN = 'loadplan.json'
"""
Name of file containing json load plan
stored within this package
"""

STYLE = 'style.cx'
"""
Name of file containing CX with style
stored within this package
"""

SIGNOR_URL = 'https://signor.uniroma2.it/'
"""
Base Signor URL
"""

GENERATED_BY_ATTRIB = 'prov:wasGeneratedBy'
"""
Network attribute to denote what created this network
"""

DERIVED_FROM_ATTRIB = 'prov:wasDerivedFrom'
"""
Network attribute to denote source of network data
"""

NORMALIZATIONVERSION_ATTRIB = '__normalizationversion'

SPECIES_MAPPING = {'9606': 'Human', '10090': 'Mouse', '10116': 'Rat'}


class NDExLoadSignorError(Exception):
    """
    Base exception for this module
    """
    pass


def get_package_dir():
    """
    Gets directory where package is installed
    :return:
    """
    return os.path.dirname(ndexsignorloader.__file__)


def get_load_plan():
    """
    Gets the load plan stored with this package

    :return: path to file
    :rtype: string
    """
    return os.path.join(get_package_dir(), LOAD_PLAN)


def get_style():
    """
    Gets the style stored with this package

    :return: path to file
    :rtype: string
    """
    return os.path.join(get_package_dir(), STYLE)


def _parse_arguments(desc, args):
    """
    Parses command line arguments
    :param desc:
    :param args:
    :return:
    """
    help_fm = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=help_fm)
    parser.add_argument('datadir', help='Directory where signor '
                                        'data is downloaded to '
                                        'and processed from')
    parser.add_argument('--profile', help='Profile in configuration '
                                          'file to use to load '
                                          'NDEx credentials which means'
                                          'configuration under [XXX] will be'
                                          'used '
                                          '(default '
                                          'ndexsignorloader)',
                        default='ndexsignorloader')
    parser.add_argument('--logconf', default=None,
                        help='Path to python logging configuration file in '
                             'this format: https://docs.python.org/3/library/'
                             'logging.config.html#logging-config-fileformat '
                             'Setting this overrides -v parameter which uses '
                             ' default logger. (default None)')

    parser.add_argument('--conf', help='Configuration file to load '
                                       '(default ~/' +
                                       NDExUtilConfig.CONFIG_FILE)
    parser.add_argument('--loadplan', help='Use alternate load plan file',
                        default=get_load_plan())
    parser.add_argument('--style',
                        help='Path to NDEx CX file to use for styling'
                             'networks',
                        default=get_style())
    parser.add_argument('--skipdownload', action='store_true',
                        help='If set, skips download of data from signor'
                             'and assumes data already resides in <datadir>'
                             'directory')
    parser.add_argument('--signorurl', default=SIGNOR_URL,
                        help='URL to signor pathways (default ' +
                        SIGNOR_URL + ')')
    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='Increases verbosity of logger to standard '
                             'error for log messages in this module and'
                             'in ' + TSV2NICECXMODULE + '. Messages are '
                             'output at these python logging levels '
                             '-v = ERROR, -vv = WARNING, -vvv = INFO, '
                             '-vvvv = DEBUG, -vvvvv = NOTSET (default no '
                             'logging)')
    parser.add_argument('--version', action='version',
                        version=('%(prog)s ' +
                                 ndexsignorloader.__version__))

    return parser.parse_args(args)


def _setup_logging(args):
    """
    Sets up logging based on parsed command line arguments.
    If args.logconf is set use that configuration otherwise look
    at args.verbose and set logging for this module and the one
    in ndexutil specified by TSV2NICECXMODULE constant
    :param args: parsed command line arguments from argparse
    :raises AttributeError: If args is None or args.logconf is None
    :return: None
    """

    if args.logconf is None:
        level = (50 - (10 * args.verbose))
        logging.basicConfig(format=LOG_FORMAT,
                            level=level)
        logging.getLogger(TSV2NICECXMODULE).setLevel(level)
        logger.setLevel(level)
        return

    # logconf was set use that file
    logging.config.fileConfig(args.logconf,
                              disable_existing_loggers=False)


class SignorDownloader(object):
    """
    Downloads signor data from site
    """
    PATHWAYDATA_SCRIPT = 'getPathwayData.php?list'

    PATHWAY_LIST_FILE = 'pathway_list.txt'
    PATHWAYDATA_DOWNLOAD_SCRIPT = 'getPathwayData.php?pathway='
    GETDATA_SCRIPT = 'getData.php?organism='
    DOWNLOAD_COMPLEXES = 'download_complexes.php'
    PROTEINFAMILY_FILE = 'SIGNOR_PF.csv'
    COMPLEXES_FILE = 'SIGNOR_complexes.csv'

    def __init__(self, signorurl, outdir):
        """
        Constructor
        :param signorurl: base SIGNOR URL
        :type signorurl: string
        :param outdir: directory where files will be downloaded to
        :type outdir: string
        """
        self._signorurl = signorurl
        self._outdir = outdir

    def get_pathway_list_file(self):
        """
        gets pathway list file
        :return:
        """
        return os.path.join(self._outdir,
                            SignorDownloader.PATHWAY_LIST_FILE)

    def get_proteinfamily_file(self):
        """
        Gets complexes file containing mapping of protein families to genes
        :return:
        """
        return os.path.join(self._outdir,
                            SignorDownloader.PROTEINFAMILY_FILE)

    def get_complexes_file(self):
        """
        Gets complexes file containing mapping of protein families to genes
        :return:
        """
        return os.path.join(self._outdir,
                            SignorDownloader.COMPLEXES_FILE)

    def _get_entity_file_map(self, entityfile):
        """
        Given a path to a semi-colon delimited file which is assumed
        to be either a SIGNOR proteinfamily or SIGNOR complexes file
        create a dictionary with key set to contents of row in second column
        and values set to comma split and trimmed list in 3rd column
        :param entityfile:
        :return:
        """
        path_map = {}
        with open(entityfile, 'r') as f:
            reader = csv.reader(f, delimiter=';')
            for line in reader:
                idlist = []
                for entry in line[2].split(','):
                    idlist.append(entry.strip())
                path_map[line[1]] = idlist
                path_map[line[0]] = idlist
        return path_map

    def get_proteinfamily_map(self):
        """

        :return:
        """
        return self._get_entity_file_map(self.get_proteinfamily_file())

    def get_complexes_map(self):
        """

        :return:
        """
        return self._get_entity_file_map(self.get_complexes_file())

    def _download_entity_file(self, entity_data_type, destfile):
        """
        Gets map of pathways
        :return: dict
        """
        logger.info('Downloading ' + entity_data_type)
        postdata = {'Content-Disposition': 'form-data; name="submit"',
                    'submit': entity_data_type}
        resp = requests.post(self._signorurl + '/' +
                             SignorDownloader.DOWNLOAD_COMPLEXES,
                             data=postdata)
        if resp.status_code != 200:
            raise NDExLoadSignorError('Got status code of ' +
                                      str(resp.status_code) +
                                      ' from signor')
        with open(destfile, 'w') as f:
            f.write(resp.text)
            f.flush()

    def _download_pathways_list(self):
        """
        Gets map of pathways
        :return: dict
        """
        logger.info("Downloading pathways list")
        resp = requests.get(self._signorurl + '/' +
                            SignorDownloader.PATHWAYDATA_SCRIPT)
        if resp.status_code != 200:
            raise NDExLoadSignorError('Got status code of ' +
                                      str(resp.status_code) + ' from signor')
        with open(self.get_pathway_list_file(), 'w') as f:
            f.write(resp.text)
            f.flush()

    def get_pathways_map(self):
        """
        Gets map from :py:const:`SignorDownloader.PATHWAY_LIST_FILE` file
        :return:
        """
        path_map = {}
        with open(self.get_pathway_list_file(), 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for line in reader:
                path_map[line[0].replace('/', '')] = line[1]

        return path_map

    def _get_download_url(self, pathway_id, relationsonly=False):
        """

        :param pathway_id:
        :param relationsonly:
        :return:
        """
        if relationsonly is False:
            relationssuffix = ''
        else:
            relationssuffix = '&relations=only'

        return self._signorurl + '/' +\
               SignorDownloader.PATHWAYDATA_DOWNLOAD_SCRIPT +\
               pathway_id + relationssuffix

    def _download_file(self, download_url, destfile):
        """

        :param theurl:
        :param destfile:
        :return:
        """
        if os.path.isfile(destfile):
            logger.info(destfile + ' exists. Skipping...')
            return

        logger.info('Downloading ' + download_url + ' to ' + destfile)
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(destfile, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)

    def _download_pathway(self, pathway_id, destfile, relationsonly=False):
        """

        :param pathway_id:
        :param destfile:
        :param relationsonly:
        :return:
        """
        download_url = self._get_download_url(pathway_id,
                                              relationsonly=relationsonly)
        self._download_file(download_url, destfile)

    def _get_fulldownload_url(self, species_id):
        """

        :param species_id:
        :return:
        """
        return self._signorurl + '/' +\
               SignorDownloader.GETDATA_SCRIPT + species_id

    def _download_fullspecies(self, species_id, destfile):
        """

        :param species_id:
        :param destfile:
        :return:
        """
        download_url = self._get_fulldownload_url(species_id)
        self._download_file(download_url, destfile)

    def download_data(self):
        """
        Downloads data
        :return:
        """
        if not os.path.isdir(self._outdir):
            os.makedirs(self._outdir, mode=0o755)

        self._download_pathways_list()
        self._download_entity_file('Download protein family data',
                                   self.get_proteinfamily_file())

        self._download_entity_file('Download complex data',
                                   self.get_complexes_file())

        path_map = self.get_pathways_map()
        for key in path_map.keys():
            self._download_pathway(key, os.path.join(self._outdir,
                                                     key + '.txt'),
                                   relationsonly=True)
            self._download_pathway(key, os.path.join(self._outdir,
                                                     key + '_desc.txt'),
                                   relationsonly=False)

        for key in SPECIES_MAPPING.keys():
            self._download_fullspecies(key,
                                       os.path.join(self._outdir,
                                                    'full_' +
                                                    SPECIES_MAPPING[key] +
                                                    '.txt'))


class DirectEdgeAttributeUpdator(NetworkUpdator):
    """
    Updates value of
    :py:const:`DirectEdgeAttributeUpdator.DIRECTED_ATTRIB`
    edge attribute

    """

    DIRECTED_ATTRIB = 'direct'

    def __init__(self):
        """
        Constructor

        """
        super(DirectEdgeAttributeUpdator, self).__init__()

    def get_description(self):
        """

        :return:
        """
        return 'Updates value of directed edge attribute to true and false'

    def update(self, network):
        """
        Iterates through all edges in network updating edge attribute
        :py:const:`DirectEdgeAttributeUpdator.DIRECTED_ATTRIB` to 'True'
        if value is 't' otherwise set it to 'False'

        :param network: network to examine
        :type network: :py:class:`~ndex2.nice_cx_network.NiceCXNetwork`
        :return: empty list
        :rtype: list
        """
        if network is None:
            return ['network is None']

        issues = []
        directed_attr_name = DirectEdgeAttributeUpdator.DIRECTED_ATTRIB
        for edge_id, edge in network.get_edges():
            edge_attr = network.get_edge_attribute(edge_id,
                                                    directed_attr_name)
            if edge_attr == (None, None):
                continue
            network.remove_edge_attribute(edge_id, directed_attr_name)
            if edge_attr['v'] == 't':

                network.set_edge_attribute(edge_id,
                                           directed_attr_name, True,
                                           type='boolean')
            else:
                network.set_edge_attribute(edge_id,
                                           directed_attr_name, False,
                                           type='boolean')

        return issues


class InvalidEdgeCitationRemover(NetworkUpdator):
    """
    Looks at citation edge attribute and removes any
    non-numeric values leaving an empty list
    """

    CITATION_ATTRIB = 'citation'

    PMC_MAP = {'PMC3619734': '15109499'}
    """
    There is one PMCID entry seen in the full networks.
    For now the above map replaces that PMC id with a 
    pubmed identifier, but in future might need to 
    setup a service to query for these from:
    
    https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=ndexsignorloader&email=my_email@example.com&ids=PMC3619734
    """

    def __init__(self):
        """
        Constructor

        """
        super(InvalidEdgeCitationRemover, self).__init__()

    def get_description(self):
        """

        :return:
        """
        return 'Removes any negative and non-numeric edge citations'

    def update(self, network):
        """
        Iterates through all edges in network removing any non-numeric
        or negative citations after pubmed: prefix is removed.

        :param network: network to examine
        :type network: :py:class:`~ndex2.nice_cx_network.NiceCXNetwork`
        :return: empty list
        :rtype: list
        """
        if network is None:
            return ['network is None']

        pmc_map = InvalidEdgeCitationRemover.PMC_MAP
        issues = []
        citation_attr_name = InvalidEdgeCitationRemover.CITATION_ATTRIB
        for edge_id, edge in network.get_edges():
            edge_attr = network.get_edge_attribute(edge_id,
                                                   citation_attr_name)
            if edge_attr == (None, None):
                continue

            update_citation = False
            updatedcitations = []
            for entry in edge_attr['v']:
                idonly = re.sub('^pubmed:', '', entry)
                # logger.info('Entry => ' +  entry + ' id: ' + idonly)
                if idonly.isdigit():
                    updatedcitations.append(entry)
                elif idonly in pmc_map:
                    update_citation = True
                    updatedcitations.append('pubmed:' +
                                            pmc_map[idonly])
                    issues.append('Replacing ' + idonly +
                                  ' with pubmed id: ' + pmc_map[idonly] +
                                  ' on edge id: ' + str(edge_id))
                else:
                    update_citation = True
                    issues.append('Removing invalid citation id: ' +
                                  str(entry) + ' on edge id: ' + str(edge_id))

            if update_citation is True:
                network.remove_edge_attribute(edge_id, citation_attr_name)
                network.set_edge_attribute(edge_id,
                                           citation_attr_name,
                                           updatedcitations,
                                           type='list_of_string')

        return issues


class UpdatePrefixesForNodeRepresents(NetworkUpdator):
    """
    Prefixes node represents with uniprot: or signor:
    based on value of :py:const:`UpdatePrefixesForNodeRepresents.DATABASE`
    node attribute
    """

    DATABASE = 'DATABASE'

    def __init__(self):
        """
        Constructor

        """
        super(UpdatePrefixesForNodeRepresents, self).__init__()

    def get_description(self):
        """

        :return:
        """
        return 'Updates value of DIRECT edge attribute to yes and no'

    def update(self, network):
        """
        Iterates through nodes and updates prefix for represents of
        node based on value of
        :py:const:`UpdatePrefixesForNodeRepresents.DATABASE` node
        attribute. If the value if 'UNIPROT' then 'uniprot:' is
        prefixed if not already there
        and if 'SIGNOR' then 'signor:' is prefixed.
        The :py:const:`UpdatePrefixesForNodeRepresents.DATABASE` is
        removed as well

        :param network: network to examine
        :type network: :py:class:`~ndex2.nice_cx_network.NiceCXNetwork`
        :return: list of node names for which no replacement was found
        :rtype: list
        """
        if network is None:
            return ['network is None']

        issues = []
        db_attribute = UpdatePrefixesForNodeRepresents.DATABASE

        for node_id, node in network.get_nodes():
            database = network.get_node_attribute_value(node_id,
                                                        db_attribute)
            represents = node.get('r')
            if database == "UNIPROT":
                if 'uniprot:' not in represents:
                    represents = "uniprot:" + represents
                    node['r'] = represents
            elif database == "SIGNOR":
                if 'signor:' not in represents:
                    represents = "signor:" + represents
                    node['r'] = represents
            # in all other cases, the identifier is already prefixed
            network.remove_node_attribute(node_id,
                                          db_attribute)

        return issues


class NodeLocationUpdator(NetworkUpdator):
    """
    Replace any empty node Compartment attribute values with cytoplasm
    """
    CYTOPLASM = 'cytoplasm'
    LOCATION = 'location'

    def __init__(self):
        """
        Constructor

        """
        super(NodeLocationUpdator, self).__init__()

    def get_description(self):
        """

        :return:
        """
        return 'Replace any empty node location attribute values with ' \
               'cytoplasm'

    def update(self, network):
        """
        Iterates through nodes and updates 'compartment' attribute
        if its empty by setting it to 'cytoplasm'

        :param network: network to examine
        :type network: :py:class:`~ndex2.nice_cx_network.NiceCXNetwork`
        :return: list of node names for which no replacement was found
        :rtype: list
        """
        if network is None:
            return ['network is None']

        issues = []
        comp_attr = NodeLocationUpdator.LOCATION
        for node_id, node in network.get_nodes():
            node_attr = network.get_node_attribute(node_id,
                                                   comp_attr)
            if node_attr == (None, None) or node_attr is None:
                logger.debug('Node ' + str(node_id) +
                             ' did not have ' + comp_attr +
                             ' attribute. Setting to ' +
                             NodeLocationUpdator.CYTOPLASM)

                network.set_node_attribute(node_id, comp_attr,
                                           NodeLocationUpdator.CYTOPLASM)
                continue
            if node_attr['v'] is None or node_attr['v'] == '':
                node_attr['v'] = NodeLocationUpdator.CYTOPLASM
        return issues


class SpringLayoutUpdator(NetworkUpdator):
    """
    Applies Spring layout
    """
    CARTESIAN_LAYOUT = 'cartesianLayout'

    PHENOTYPESLIST = 'phenotypesList'
    FACTOR = 'factor'
    CYTOPLASM = 'cytoplasm'
    RECEPTOR = 'receptor'
    EXTRACELLULAR = 'extracellular'

    def __init__(self, scale=500.0,
                 iterations=10, seed=10,
                 location_weight=5.0):
        """
        Constructor

        :param scale: scale for networkx spring layout
        :type scale: float
        """
        super(SpringLayoutUpdator, self).__init__()

        self._scale = scale
        self._seed = seed
        self._iterations = iterations
        self._min = -scale
        self._max = scale
        self._location_weight = location_weight
        random.seed(self._seed)

    def get_description(self):
        """

        :return:
        """
        return 'Applies Spring layout to network'

    def _get_random_x_position(self):
        """

        :return:
        """
        return random.uniform(self._min, self._max)

    def _get_initial_node_positions(self, network):
        """
        Based on Compartment node attribute position nodes

        :param network:
        :return:
        """
        node_pos = {}
        compartment = NodeLocationUpdator.LOCATION
        for nodeid, node in network.get_nodes():
            node_attr = network.get_node_attribute(nodeid,
                                                   compartment)
            if node_attr is None:
                continue
            if node_attr['v'] == SpringLayoutUpdator.EXTRACELLULAR:
                node_pos[nodeid] = (self._get_random_x_position(),
                                    self._min)
            elif node_attr['v'] == SpringLayoutUpdator.RECEPTOR:
                node_pos[nodeid] = (self._get_random_x_position(),
                                    self._min/2.0)
            elif node_attr['v'] == SpringLayoutUpdator.CYTOPLASM:
                node_pos[nodeid] = (self._get_random_x_position(), 0.0)
            elif node_attr['v'] == SpringLayoutUpdator.FACTOR:
                node_pos[nodeid] = (self._get_random_x_position(),
                                    self._max/2.0)
            elif node_attr['v'] == SpringLayoutUpdator.PHENOTYPESLIST:
                node_pos[nodeid] = (self._get_random_x_position(),
                                    self._max)

        node_pos[SpringLayoutUpdator.EXTRACELLULAR] = (0.0, self._min)
        node_pos[SpringLayoutUpdator.RECEPTOR] = (0.0, self._min/2.0)
        node_pos[SpringLayoutUpdator.CYTOPLASM] = (0.0, 0.0)
        node_pos[SpringLayoutUpdator.FACTOR] = (0.0, self._max/2.0)
        node_pos[SpringLayoutUpdator.PHENOTYPESLIST] = (0.0, self._max)

        return node_pos

    def _get_cartesian_aspect(self, net_x):
        """
        Converts coordinates from :py:class:`networkx.Graph`
        to NDEx aspect
        :param net_x: network with coordinates
        :type net_x: :py:class:`networkx.Graph`
        :return: coordinates as list of dicts ie
                 [{'node': <id>, 'x': <xpos>, 'y': <ypos>}]
        :rtype: list
        """
        # return [{'node': n,
        #         'x': float(net_x.pos[n][0]),
        #         'y': float(net_x.pos[n][1])} for n in net_x.pos]
        coords = []
        for n in net_x.pos:
            if not isinstance(n, int):
                continue
            coords.append({'node': n,
                           'x': float(net_x.pos[n][0]),
                           'y': float(net_x.pos[n][1])})
        return coords

    def _get_networkx_object(self, network):
        """

        :param network:
        :return:
        """
        net_x = network.to_networkx(mode='default')
        net_x.add_node(SpringLayoutUpdator.EXTRACELLULAR,
                       weight=self._location_weight)
        net_x.add_node(SpringLayoutUpdator.RECEPTOR,
                       weight=self._location_weight)
        net_x.add_node(SpringLayoutUpdator.CYTOPLASM,
                       weight=self._location_weight)
        net_x.add_node(SpringLayoutUpdator.FACTOR,
                       weight=self._location_weight)
        net_x.add_node(SpringLayoutUpdator.PHENOTYPESLIST,
                       weight=self._location_weight)

        compartment = NodeLocationUpdator.LOCATION

        for nodeid, node in network.get_nodes():
            node_attr = network.get_node_attribute(nodeid,
                                                   compartment)
            if node_attr is None:
                continue
            if node_attr['v'] is not None:
                net_x.add_edge(nodeid, node_attr['v'])
        return net_x

    def update(self, network):
        """
        Applies spring layout to network

        :param network: network to examine
        :type network: :py:class:`~ndex2.nice_cx_network.NiceCXNetwork`
        :return: list of node names for which no replacement was found
        :rtype: list
        """
        if network is None:
            return ['network is None']

        issues = []

        net_x = self._get_networkx_object(network)

        numnodes = len(network.get_nodes())
        updatedscale = self._scale - numnodes
        updatedk = 1000.0 + numnodes*20
        pos_dict = self._get_initial_node_positions(network)
        net_x.pos = networkx.drawing.spring_layout(net_x, scale=updatedscale,
                                                   seed=self._seed,
                                                   pos=pos_dict,
                                                   k=updatedk,
                                                   iterations=self._iterations)

        network.set_opaque_aspect(SpringLayoutUpdator.CARTESIAN_LAYOUT,
                                  self._get_cartesian_aspect(net_x))
        return issues


class NodeMemberUpdator(NetworkUpdator):
    """
    Adds genes to 'member' attribute for any nodes that
    are of type 'complex', 'proteinfamily'
    """
    TYPE = 'type'
    MEMBER = 'member'
    PROTEINFAMILY = 'proteinfamily'
    COMPLEX = 'complex'
    SIGNOR_PF_PREFIX = 'SIGNOR-PF'
    SIGNOR_C_PREFIX = 'SIGNOR-C'

    def __init__(self, proteinfamily_map, complexes_map,
                 genesearcher=GeneSymbolSearcher()):
        """
        Constructor

        """
        super(NodeMemberUpdator, self).__init__()
        self._proteinfamilymap = proteinfamily_map
        self._complexesmap = complexes_map
        self._genesearcher = genesearcher

    def get_description(self):
        """

        :return:
        """
        return 'Add genes to member node attribute for complexes and protein ' \
               'families'

    def _add_member_genes(self, network, node, proteinlist):
        """

        :param network:
        :param node:
        :param proteinlist:
        :return:
        """

        if proteinlist is None or len(proteinlist) == 0:
            return ['No proteins obtained for node: ' + str(node)]

        issues = []
        memberlist = []
        for entry in proteinlist:
            g_symbol = self._genesearcher.get_symbol(entry)
            if g_symbol is None or g_symbol == '':
                issues.append('For node ' + str(node) +
                              ' No gene symbol found for ' +
                              str(entry) + '. Skipping.')
                continue

            memberlist.append('hgnc.symbol:' + g_symbol)
        if len(memberlist) == 0:
            issues.append('Not a single gene symbol found. Skipping '
                          'insertion of member attribute for node ' +
                          str(node))
            return issues

        network.set_node_attribute(node['@id'], NodeMemberUpdator.MEMBER,
                                   memberlist,
                                   type='list_of_string', overwrite=True)
        return issues

    def _replace_signor_ids(self, proteinlist):
        """
        Iterate through 'proteinlist` and if any entries start
        with SIGNOR-PF or SIGNOR-C do another lookup in proteinfamilymap
        or complexesmap set in constructor for the genes. If found add
        these genes to the list.
        :param proteinlist:
        :return:
        """
        updatedlist = []
        issues = []
        for entry in proteinlist:
            if entry.startswith(NodeMemberUpdator.SIGNOR_PF_PREFIX):
                if entry not in self._proteinfamilymap:
                    issues.append('Protein id: ' + entry +
                                  ' matched prefix ' +
                                  NodeMemberUpdator.SIGNOR_PF_PREFIX +
                                  ' which is assumed to be a reference '
                                  'to another'
                                  ' entry, but none found. Skipping.')
                    continue
                updatedlist.extend(self._proteinfamilymap[entry])
                continue
            elif entry.startswith(NodeMemberUpdator.SIGNOR_C_PREFIX):
                if entry not in self._complexesmap:
                    issues.append('Protein id: ' + entry + ' matched prefix ' +
                                  NodeMemberUpdator.SIGNOR_C_PREFIX +
                                  ' which is assumed to be a '
                                  'reference to another'
                                  ' entry, but none found. Skipping.')
                    continue
                updatedlist.extend(self._complexesmap[entry])
                continue
            updatedlist.append(entry)
        return list(set(updatedlist)), issues

    def update(self, network):
        """
        Iterates through nodes and updates 'member' attribute
        for nodes with 'type' attribute set to 'proteinfamily' or 'complex'
        by getting mapping from signor

        :param network: network to examine
        :type network: :py:class:`~ndex2.nice_cx_network.NiceCXNetwork`
        :return: list of node names for which no replacement was found
        :rtype: list
        """
        if network is None:
            return ['network is None']

        issues = []
        type_attr = NodeMemberUpdator.TYPE
        for node_id, node in network.get_nodes():
            node_attr = network.get_node_attribute(node_id,
                                                   type_attr)
            if node_attr == (None, None) or node_attr is None:
                logger.debug('Node ' + str(node_id) +
                             ' did not have ' + type_attr +
                             ' attribute.')
                continue
            if node_attr['v'] == NodeMemberUpdator.PROTEINFAMILY:
                if node['n'] not in self._proteinfamilymap:
                    logger.error('Node: ' + node['n'] +
                                 ' not in proteinfamily map')
                    issues.append('No entry in proteinfamily map for node: ' +
                                  str(node))
                    continue
                proteinlist, oissues = self._replace_signor_ids(self._proteinfamilymap[node['n']])
                issues.extend(oissues)
                issues.extend(self._add_member_genes(network, node,
                                                     proteinlist))
            elif node_attr['v'] == NodeMemberUpdator.COMPLEX:
                if node['n'] not in self._complexesmap:
                    logger.error('Node: ' + node['n'] + ' not in complexes map')
                    issues.append('No entry in complexes map for node: ' +
                                  str(node))
                    continue
                proteinlist, oissues = self._replace_signor_ids(self._complexesmap[node['n']])
                issues.extend(oissues)
                issues.extend(self._add_member_genes(network, node,
                                                     proteinlist))
        return issues


class LoadSignorIntoNDEx(object):
    """
    Class to load content
    """

    DISEASE_PATHWAYS = ['ALZHEIMER DISEASE', 'FSGS', 'NOONAN SYNDROME',
                        'PARKINSON DISEASE']

    CANCER_PATHWAYS = ['ACUTE MYELOID LEUKEMIA', 'COLORECTAL CARCINOMA',
                       'GLIOBLASTOMA MULTIFORME', 'LUMINAL BREAST CANCER',
                       'MALIGNANT MELANOMA', 'PROSTATE CANCER',
                       'RHABDOMYOSARCOMA', 'THYROID CANCER']

    def __init__(self, args,
                 downloader,
                 updators=None):
        """

        :param args:
        """
        self._conf_file = args.conf
        self._args = args
        self._profile = args.profile
        self._outdir = os.path.abspath(args.datadir)
        self._user = None
        self._pass = None
        self._server = None
        self._ndex = None
        self._loadplan = None
        self._full_loadplan = None
        self._template = None
        self._net_summaries = None
        self._downloader = downloader
        self._updators = updators

    def _parse_config(self):
            """
            Parses config
            :return:
            """
            ncon = NDExUtilConfig(conf_file=self._conf_file)
            con = ncon.get_config()
            self._user = con.get(self._profile, NDExUtilConfig.USER)
            self._pass = con.get(self._profile, NDExUtilConfig.PASSWORD)
            self._server = con.get(self._profile, NDExUtilConfig.SERVER)

    def _get_user_agent(self):
        """
        Builds user agent string
        :return: user agent string in form of ncipid/<version of this tool>
        :rtype: string
        """
        return 'ndexsignorloader/' + self._args.version

    def _create_ndex_connection(self):
        """
        creates connection to ndex
        :return:
        """
        if self._ndex is None:
            self._ndex = Ndex2(host=self._server, username=self._user,
                               password=self._pass,
                               user_agent=self._get_user_agent())

    def _parse_load_plan(self):
        """

        :return:
        """
        with open(self._args.loadplan, 'r') as f:
            self._loadplan = json.load(f)

        self._full_loadplan = copy.deepcopy(self._loadplan)
        self._full_loadplan['source_plan']['property_columns'].remove({'column_name': 'REGULATOR_LOCATION',
                                                                       'attribute_name': 'location'})
        self._full_loadplan['target_plan']['property_columns'].remove({'column_name': 'TARGET_LOCATION',
                                                                      'attribute_name': 'location'})

    def _load_style_template(self):
        """
        Loads the CX network specified by self._args.style into self._template
        :return:
        """
        self._template = ndex2.create_nice_cx_from_file(os.path.abspath(self._args.style))

    def _load_network_summaries_for_user(self):
        """
        Gets a dictionary of all networks for user account
        <network name upper cased> => <NDEx UUID>
        :return: dict
        """
        net_summaries = self._ndex.get_network_summaries_for_user(self._user)
        self._net_summaries = {}
        for nk in net_summaries:
            if nk.get('name') is not None:
                self._net_summaries[nk.get('name').upper()] = nk.get('externalId')

    def _get_signor_pathway_relations_df(self, pathway_id,
                                         is_full_pathway=False):
        """
        Loads SIF file `pathway_id`.txt from output directory specified
        in constructor via Pandas.

        :param pathway_id: Prefix of file to load
        :param is_full_pathway: If true it is assumed the pathway_id file
                                is a full network and a custom set of
                                columns is passed to Pandas and a filter
                                is applied removing any entries that are
                                not human
        :return: Pandas data frame of data
        """
        pathway_file_path = os.path.join(self._outdir, pathway_id + '.txt')
        if not os.path.isfile(pathway_file_path):
            raise NDExLoadSignorError(pathway_file_path +
                                      ' file missing.')
        if os.path.getsize(pathway_file_path) < 10:
            raise NDExLoadSignorError(pathway_file_path +
                                      ' looks to be empty')
        usecols = None
        index_col = None
        if is_full_pathway is True:
            logger.info('Full pathway detected, setting columns for pandas')
            usecols = ['entitya', 'typea', 'ida', 'databasea', 'entityb',
                       'typeb', 'idb', 'databaseb', 'effect', 'mechanism',
                       'residue', 'sequence', 'tax_id', 'cell_data',
                       'tissue_data', 'modulator_complex', 'target_complex',
                       'modificationa', 'modaseq', 'modificationb', 'modbseq',
                       'pmid', 'direct', 'notes', 'annotator', 'sentence',
                       'signor_id']
            index_col = False

        with open(pathway_file_path, 'r', encoding='utf-8') as pfp:
            df = pd.read_csv(pfp, dtype=str, na_filter=False,
                             delimiter='\t', names=usecols,
                             index_col=index_col, engine='python')

            # remove rows that are not human
            # (taken from load-content/signor/process_signor.py)
            # not sure if this does that
            if is_full_pathway is True:
                filtered = df[(df["entitya"] != "") &
                              (df["entityb"] != "") &
                              (df["ida"] != "") &
                              (df["idb"] != "")]
                logger.info('Original data frame had: ' +
                            str(len(df.index)) + ' rows and filtered has: ' +
                            str(len(filtered.index)) + ' rows')
                return filtered
            return df

    def _get_signor_pathway_description_df(self, pathway_id):
        pathway_file_path = os.path.join(self._outdir,
                                         pathway_id + '_desc.txt')
        if not os.path.isfile(pathway_file_path):
            raise NDExLoadSignorError(pathway_file_path + ' file missing.')

        with open(pathway_file_path, 'r', encoding='utf-8') as pfp:
            signor_pathway_relations_df = pd.read_csv(pfp, dtype=str,
                                                      na_filter=False,
                                                      delimiter='\t',
                                                      engine='python')

            return signor_pathway_relations_df

    def _add_node_types_in_network_to_report(self, network, report):
        """
        Adds node types to report
        :param network:
        :param report:
        :return: None
        """
        for i, node in network.get_nodes():
            val = network.get_node_attribute_value(i, 'type')
            report.add_nodetype(val)

    def _process_pathway(self, pathway_id, pathway_name):
        """

        :param pathway_id:
        :return:
        """
        is_full_pathway = False
        loadplan = self._loadplan
        if pathway_name.startswith('Signor Full'):
            is_full_pathway = True
            loadplan = self._full_loadplan

        df = self._get_signor_pathway_relations_df(pathway_id,
                                                   is_full_pathway=is_full_pathway)
        # upcase column names
        rename = {}
        for column_name in df.columns:
            rename[column_name] = column_name.upper()
        df = df.rename(columns=rename)

        network = t2n.convert_pandas_to_nice_cx_with_load_plan(df,
                                                               loadplan)
        report = NetworkIssueReport(pathway_name)

        self._add_pathway_info(network, pathway_id,
                               is_full_pathway=is_full_pathway,
                               pathway_name=pathway_name)

        if self._updators is not None:
            for updator in self._updators:
                issues = updator.update(network)
                report.addissues(updator.get_description(), issues)

        # apply style to network
        network.apply_style_from_network(self._template)

        network_update_key = self._net_summaries.get(network.get_name().upper())

        self._add_node_types_in_network_to_report(network, report)

        if network_update_key is not None:
            network.update_to(network_update_key, self._server,
                              self._user, self._pass,
                              user_agent=self._get_user_agent())
        else:
            network.upload_to(self._server, self._user,
                              self._pass,
                              user_agent=self._get_user_agent())
        return report

    def _set_generatedby_in_network_attributes(self, network):
        """
        Sets the network attribute :py:const:`GENERATED_BY_ATTRIB`
        with ndexncipidloader <VERSION>
        :param network: network to add attribute
        :type :py:class:`~ndex2.nice_cx_network.NiceCXNetwork`
        :return: None
        """
        network.set_network_attribute(GENERATED_BY_ATTRIB,
                                      '<a href="https://github.com/'
                                      'ndexcontent/ndexsignorloader"'
                                      '>ndexsignorloader ' +
                                      str(ndexsignorloader.__version__) +
                                      '</a>')

    def _set_normalization_version(self, network):
        """
        Sets the network attribute :py:const:`NORMALIZATIONVERSION`
        with 0.1
        :param network: network to add attribute
        :type :py:class:`~ndex2.nice_cx_network.NiceCXNetwork`
        :return: None
        """
        network.set_network_attribute(NORMALIZATIONVERSION_ATTRIB, '0.1')

    def _set_wasderivedfrom(self, network, pathway_id,
                            is_full_pathway=False):
        """
        Sets the 'prov:wasDerivedBy' network attribute to the
        ftp location containing the OWL file for this network.
        The ftp information is pulled from :py:const:`DEFAULT_FTP_HOST` and
         :py:const:`DEFAULT_FTP_DIR` and the owl file name is the
         name of the network with .owl.gz appended

        :param network: network to add attribute
        :type :py:class:`~ndex2.nice_cx_network.NiceCXNetwork`
        :return: None
        """
        derivedurl = 'https://signor.uniroma2.it'
        if is_full_pathway is False:
            derivedurl = derivedurl +\
                         '/pathway_browser.php?organism=&' +\
                         'pathway_list=' + str(pathway_id)

        network.set_network_attribute(DERIVED_FROM_ATTRIB, derivedurl)

    def _set_type(self, network):
        """
        Sets type network attribute adding a list with 'pathway' and an additional
        value based on name of network.
        :param network: network to update
        :type network: :py:class:`~ndex2.nice_cx_network.NiceCXNetwork`
        :return: None
        """
        typedata = ['pathway']
        if network.get_name().upper() in LoadSignorIntoNDEx.DISEASE_PATHWAYS:
            typedata.append("Disease Pathway")
        elif network.get_name().upper() in LoadSignorIntoNDEx.CANCER_PATHWAYS:
            typedata.append("Cancer Pathway")
        else:
            typedata.append("Signalling Pathway")
        network.set_network_attribute('type', typedata, type='list_of_string')

    def _add_pathway_info(self, network, pathway_id,
                          is_full_pathway=False,
                          pathway_name=None):
        """
        Adds network
        :param network:
        :param network_id:
        :param cytoscape_visual_properties_template_id: UUID of NDEx
               network to
               extract various network attributes such as description,
               rightsHolder, reference, rights

        :return:
        """
        if is_full_pathway is False:
            dataframe = self._get_signor_pathway_description_df(pathway_id)
            if dataframe is None:
                logger.warning('Skipping ' + pathway_id)
                return
            if not pd.isnull(dataframe.iat[0, 1]):
                network.set_name(dataframe.iat[0, 1])
            if not pd.isnull(dataframe.iat[0, 0]):
                network.set_network_attribute("labels", [dataframe.iat[0, 0]],
                                              type='list_of_string')
            if not pd.isnull(dataframe.iat[0, 3]):
                auth_val = dataframe.iat[0, 3]
                if auth_val is not None and len(auth_val) > 0:
                    network.set_network_attribute("author",
                                                  dataframe.iat[0, 3])
            if not pd.isnull(dataframe.iat[0, 2]):
                network.set_network_attribute("description",
                                              '%s' % (dataframe.iat[0, 2]))
            network.set_network_attribute("organism", "Homo Sapiens (human)")
        else:
            logger.info("Full pathway detected: " + str(pathway_name))
            network.set_name(pathway_name)

            net_organism = 'Unknown'
            if 'Human' in pathway_id:
                net_organism = 'Human'
                network.set_network_attribute("organism", "Homo sapiens (human)")
            elif 'Rat' in pathway_id:
                net_organism = 'Rat'
                network.set_network_attribute("organism", "Rattus norvegicus (rat)")
            elif 'Mouse' in pathway_id:
                net_organism = 'Mouse'
                network.set_network_attribute("organism", "Mus musculus (mouse)")
            else:
                logger.error('No matching organism found for: ' + pathway_id)

            network.set_network_attribute('description',
                                          'This network contains all the ' +
                                          net_organism +
                                          ' interactions currently available '
                                          'in SIGNOR')

        network.set_network_attribute('rightsHolder', 'Prof. Gianni Cesareni ')
        network.set_network_attribute('rights',
                                      'Attribution-ShareAlike 4.0 '
                                      'International (CC BY-SA 4.0)')

        network.set_network_attribute("reference",
                                      '<div>Perfetto L., <i>et al.</i></div>'
                                      '<div><b>SIGNOR: a database of causal '
                                      'relationships between biological '
                                      'entities</b><i>.</i></div><div>Nucleic '
                                      'Acids Res. 2016 Jan 4;44(D1):D548-54'
                                      '</div><div><span><a href=\"\\&#34;'
                                      'https://doi.org/10.1093/nar/gkv1048'
                                      '\\&#34;\" target=\"\\&#34;\\&#34;\">'
                                      'doi: 10.1093/nar/gkv1048</a></span>'
                                      '</div>')

        network.set_network_attribute("version", f"{datetime.now():%d-%b-%Y}")

        # set type network attribute
        self._set_type(network)

        # set provenance for network
        self._set_generatedby_in_network_attributes(network)

        # set normalization version for network
        self._set_normalization_version(network)

        # set was derived from
        self._set_wasderivedfrom(network, str(pathway_id),
                                 is_full_pathway=is_full_pathway)

    def run(self):
        """
        Runs content loading for NDEx Signor Content Loader
        :param theargs:
        :return:
        """
        self._parse_config()
        logger.debug('Parsed config: ' + self._user)
        self._parse_load_plan()
        self._create_ndex_connection()
        self._load_network_summaries_for_user()
        self._load_style_template()
        report_list = []

        pathway_map = self._downloader.get_pathways_map()
        if pathway_map is None:
            logger.error('Pathway map came back as None')
            return 1
        for key in pathway_map.keys():
            logger.info('Processing ' + key + ' => ' + pathway_map[key])
            try:
                report_list.append(self._process_pathway(key, pathway_map[key]))
            except NDExLoadSignorError as ne:
                logger.exception('Unable to load pathway: ' + key +
                                 ' => ' + pathway_map[key])

        # process full pathways
        for orgname in ['Human', 'Mouse', 'Rat']:
            pname = 'Signor Full ' + orgname
            logger.info('Processing full ' + pname)
            try:
                report_list.append(self._process_pathway('full_' + orgname,
                                                         pname))
            except NDExLoadSignorError as ne:
                logger.exception('Unable to load pathway: ' +
                                 'full_' + orgname + '.txt')

        node_type = set()
        for entry in report_list:
            for nt in entry.get_nodetypes():
                node_type.add(nt)
            sys.stdout.write(entry.get_fullreport_as_string())

        sys.stdout.write('Node Types Found in all networks:\n')
        for entry in node_type:
            sys.stdout.write('\t' + entry + '\n')

        return 0


def main(args):
    """
    Main entry point for program
    :param args:
    :return:
    """
    desc = """
    Version {version}

    Loads NDEx Signor Content Loader data into NDEx (http://ndexbio.org).
    
    To connect to NDEx server a configuration file must be passed
    into --conf parameter. If --conf is unset the configuration 
    path ~/{confname} is examined. 
         
    The configuration file should be formatted as follows:
         
    [<value in --profile (default ncipid)>]
         
    {user} = <NDEx username>
    {password} = <NDEx password>
    {server} = <NDEx server(omit http) ie public.ndexbio.org>
    
    For more information on what operations are performed
    visit: https://github.com/ndexcontent/ndexsignorloader

    """.format(confname=NDExUtilConfig.CONFIG_FILE,
               user=NDExUtilConfig.USER,
               password=NDExUtilConfig.PASSWORD,
               server=NDExUtilConfig.SERVER,
               version=ndexsignorloader.__version__)
    theargs = _parse_arguments(desc, args[1:])
    theargs.program = args[0]
    theargs.version = ndexsignorloader.__version__

    try:
        _setup_logging(theargs)
        datadir = os.path.abspath(theargs.datadir)
        downloader = SignorDownloader(theargs.signorurl,
                                      datadir)
        if theargs.skipdownload is False:
            downloader.download_data()

        updators = [DirectEdgeAttributeUpdator(),
                    UpdatePrefixesForNodeRepresents(),
                    NodeLocationUpdator(),
                    NodeMemberUpdator(downloader.get_proteinfamily_map(),
                                      downloader.get_complexes_map()),
                    InvalidEdgeCitationRemover(),
                    SpringLayoutUpdator()]
        loader = LoadSignorIntoNDEx(theargs, downloader,
                                    updators=updators)
        return loader.run()
    except Exception as e:
        logger.exception('Caught exception')
        return 2
    finally:
        logging.shutdown()


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
