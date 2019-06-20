#!python

import argparse
import sys
import logging
from logging import config
from ndexutil.config import NDExUtilConfig
import ndexstringloader

import csv
import pandas as pd

from datetime import datetime

import gzip
import shutil

import os


from ndexutil.tsv.streamtsvloader import StreamTSVLoader


import requests

import ndex2


logger = logging.getLogger(__name__)

TSV2NICECXMODULE = 'ndexutil.tsv.tsv2nicecx2'

LOG_FORMAT = "%(asctime)-15s %(levelname)s %(relativeCreated)dms " \
             "%(filename)s::%(funcName)s():%(lineno)d %(message)s"


STRING_LOAD_PLAN = 'string_plan.json'

def get_package_dir():
    """
    Gets directory where package is installed
    :return:
    """
    return os.path.dirname(ndexstringloader.__file__)

def get_load_plan():
    """
    Gets the load plan stored with this package
    :return: path to file
    :rtype: string
    """
    return os.path.join(get_package_dir(), STRING_LOAD_PLAN)

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

    parser.add_argument('--profile', help='Profile in configuration '
                                          'file to load '
                                          'NDEx credentials which means'
                                          'configuration under [XXX] will be'
                                          'used '
                                          '(default '
                                          'ndexstringloader)',
                        required=True)
    parser.add_argument('--logconf', default=None,
                        help='Path to python logging configuration file in '
                             'this format: https://docs.python.org/3/library/logging.config.html#logging-config-fileformat'
                             'Setting this overrides -v parameter which uses '
                             ' default logger. (default None)')

    parser.add_argument('--conf', help='Configuration file to load '
                                       '(default ~/' +
                                       NDExUtilConfig.CONFIG_FILE)
    parser.add_argument('--loadplan', help='Load plan json file', default=get_load_plan())
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
                                 ndexstringloader.__version__))

    parser.add_argument('--stringversion', help='Version of STRING DB', required=True)

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


class NDExNdexstringloaderLoader(object):
    """
    Class to load content
    """
    def __init__(self, args):
        """
        :param args:
        """
        self._conf_file = args.conf
        self._profile = args.profile
        self._load_plan = args.loadplan

        self._string_version = args.stringversion

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

        self._template_id = con.get('network_ids', 'style')
        self._hi_conf_template_id = con.get('network_ids', 'hi_confidence_style')
        self._network_id = con.get('network_ids', 'full')
        self._hi_conf_network_id = con.get('network_ids', 'hi_confidence')

        self._protein_links_url = con.get('source', 'ProteinLinksFile')
        self._names_file_url = con.get('source', 'NamesFile')
        self._entrez_ids_file_url = con.get('source', 'EntrezIdsFile')
        self._uniprot_ids_file_url = con.get('source', 'UniprotIdsFile')

        self._full_file_name = con.get('input', 'full_file_name')
        self._entrez_file = con.get('input', 'entrez_file')
        self._names_file = con.get('input', 'names_file')
        self._uniprot_file = con.get('input', 'uniprot_file')

        self._output_tsv_file_name = con.get('output', 'output_tsv_file_name')
        self._output_hi_conf_tsv_file_name = con.get('output', 'output_hi_conf_tsv_file_name')


    def _download(self, url, local_file_name):

        print('{} - downloading {} to {}...'.format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), url, local_file_name))

        r = requests.get(url)
        with open(local_file_name, "wb") as code:
            code.write(r.content)
            print('{} - downloaded {} to {}\n'.format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), url, local_file_name))


    def _unzip(self, local_file_name):
        zip_file = local_file_name + '.gz'

        print('{} - unzipping and then removing {}...'.format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), zip_file))

        with gzip.open(zip_file, 'rb') as f_in:
            with open(local_file_name, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        os.remove(zip_file)
        print('{} - {} unzipped and removed\n'.format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), zip_file))


    def _download_STRING_files(self):
        """
        Parses config
        :return:
        """
        self._download(self._protein_links_url, self._full_file_name + '.gz')
        self._download(self._names_file_url, self._names_file + '.gz')
        self._download(self._entrez_ids_file_url, self._entrez_file + '.gz')
        self._download(self._uniprot_ids_file_url, self._uniprot_file + '.gz')

    def _unpack_STRING_files(self):
        """
        Parses config
        :return:
        """
        self._unzip(self._full_file_name)
        self._unzip(self._entrez_file)
        self._unzip(self._names_file)
        self._unzip(self._uniprot_file)

    def _get_name_rep_alias(self, ensembl_protein_id, ensembl_ids):
        name_rep_alias = ensembl_ids[ensembl_protein_id]
        use_ensembl_id_for_represents = False

        if name_rep_alias['display_name'] is None:
            use_ensembl_id_for_represents = True
            name_rep_alias['display_name'] = 'ensembl:' + ensembl_protein_id.split('.')[1]

        if name_rep_alias['represents'] is None:
            if use_ensembl_id_for_represents:
                name_rep_alias['represents'] = name_rep_alias['display_name']
            else:
                name_rep_alias['represents'] = 'hgnc:' + name_rep_alias['display_name']

        if name_rep_alias['alias'] is None:
            if use_ensembl_id_for_represents:
                name_rep_alias['alias'] = name_rep_alias['display_name']
            else:
                name_rep_alias['alias'] = name_rep_alias['represents']

        ret_str = \
            name_rep_alias['display_name'] + '\t' + \
            name_rep_alias['represents'] + '\t' + \
            name_rep_alias['alias']

        return ret_str

    def run(self):
        """
        Runs content loading for NDEx STRING Content Loader
        :param theargs:
        :return:
        """
        self._parse_config()

        self._download_STRING_files()

        self._unpack_STRING_files()


        ensembl_ids = {}
        duplicate_display_names = {}
        duplicate_uniprot_ids = {}

        output_tsv_file_columns = [
            "name1",
            "represents1",
            "alias1",
            "name2",
            "represents2",
            "alias2",
            "neighborhood",
            "neighborhood_transferred",
            "fusion",
            "cooccurence",
            "homology",
            "coexpression",
            "coexpression_transferred",
            "experiments",
            "experiments_transferred",
            "database",
            "database_transferred",
            "textmining",
            "textmining_transferred",
            "combined_score"
        ]

        print('\nLoading {} for reading...'.format(self._full_file_name))

        with open(self._full_file_name, 'r') as f:
            d_reader = csv.DictReader(f)
            headers = ((d_reader.fieldnames)[0]).split()

        print('{} loaded\n'.format(self._full_file_name))

        print('Preparing a dictionary of Ensembl Ids ...')

        for i in range(2):
            df = pd.read_csv(self._full_file_name, sep='\s+', skipinitialspace=True, usecols=[headers[i]])
            df.sort_values(headers[i], inplace=True)
            df.drop_duplicates(subset=headers[i], keep='first', inplace=True)

            for index, row in df.iterrows():
                ensembl_ids[row[headers[i]]] = {}
                ensembl_ids[row[headers[i]]]['display_name'] = None
                ensembl_ids[row[headers[i]]]['alias'] = None
                ensembl_ids[row[headers[i]]]['represents'] = None

        print('Found {:,} unique Ensembl Ids in {}\n'.format(len(ensembl_ids), self._full_file_name))



        #populate name - 4.display name -> becomes name

        print('Populating display names from {}...'.format(self._names_file))
        row_count = 0

        with open(self._names_file, 'r') as f:
            next(f)
            row1 = csv.reader(f, delimiter=' ')
            for row in row1:
                columns_in_row = row[0].split()
                ensembl_id = columns_in_row[2]
                display_name = columns_in_row[1]

                if ensembl_id in ensembl_ids:

                    if (ensembl_ids[ensembl_id]['display_name'] is None):
                        ensembl_ids[ensembl_id]['display_name'] = display_name

                    elif display_name != ensembl_ids[ensembl_id]['display_name']:
                        # duplicate: we found entries in human.name_2_string.tsv where same Ensembl Id maps to
                        # multiple display name.  This should never happen though
                        if ensembl_id not in duplicate_display_names:
                            duplicate_display_names[ensembl_id] = []
                            duplicate_display_names[ensembl_id].append(ensembl_ids[ensembl_id]['display_name'])

                        duplicate_display_names[ensembl_id].append(display_name)

                row_count = row_count + 1;

        print('Populated {:,} display names from {}\n'.format(row_count, self._names_file))


        # populate alias - 3. node string id -> becomes alias, for example
        # ensembl:ENSP00000000233|ncbigene:857

        print('Populating aliases from {}...'.format(self._entrez_file))
        row_count = 0

        with open(self._entrez_file, 'r') as f:
            next(f)
            row1 = csv.reader(f, delimiter=' ')
            for row in row1:
                columns_in_row = row[0].split()
                ensembl_id = columns_in_row[2]
                ncbi_gene_id = columns_in_row[1]

                if ensembl_id in ensembl_ids:

                    if (ensembl_ids[ensembl_id]['alias'] is None):

                        ensembl_alias = 'ensembl:' + ensembl_id.split('.')[1]

                        # ncbi_gene_id can be |-separated list, for example, '246721|548644'
                        ncbi_gene_id_split = ncbi_gene_id.split('|')

                        ncbi_gene_id_split = ['ncbigene:' + element + '|' for element in ncbi_gene_id_split]

                        if (len(ncbi_gene_id_split) > 1):
                            alias_string = "".join(ncbi_gene_id_split) + ensembl_alias
                        else:
                            alias_string = ncbi_gene_id_split[0] + ensembl_alias

                        ensembl_ids[ensembl_id]['alias'] = alias_string

                    else:
                        pass

                row_count = row_count + 1;

        print('Populated {:,} aliases from {}\n'.format(row_count, self._entrez_file))


        print('Populating represents from {}...'.format(self._uniprot_file))
        row_count = 0

        with open(self._uniprot_file, 'r') as f:
            next(f)
            row1 = csv.reader(f, delimiter=' ')
            for row in row1:
                columns_in_row = row[0].split()
                ensembl_id = columns_in_row[2]
                uniprot_id = columns_in_row[1].split('|')[0]

                if ensembl_id in ensembl_ids:

                    if (ensembl_ids[ensembl_id]['represents'] is None):
                        ensembl_ids[ensembl_id]['represents'] = 'uniprot:' + uniprot_id

                    elif uniprot_id != ensembl_ids[ensembl_id]['represents']:
                        # duplicate: we found entries in human.uniprot_2_string.tsv where same Ensembl Id maps to
                        # multiple uniprot ids.
                        if ensembl_id not in duplicate_uniprot_ids:
                            duplicate_uniprot_ids[ensembl_id] = []
                            duplicate_uniprot_ids[ensembl_id].append(ensembl_ids[ensembl_id]['represents'])

                            duplicate_uniprot_ids[ensembl_id].append(uniprot_id)

                row_count = row_count + 1;

        print('Populated {:,} represents from {}\n'.format(row_count, self._uniprot_file))



        # iterate over ensembl_ids and see if there is any unresolved
        # display names, aliases or represents

        #for key, value in ensembl_ids.items():
        #    k, v = key, value

        #    if value['display_name'] is None or value['alias'] is None or value['represents'] is None:
        #        print('For {} values are {}'.format(key, value))


        # generate output tsv files: one general and one high confidence
        print('Creating target {} and {} files...'.format(self._output_tsv_file_name, self._output_hi_conf_tsv_file_name))


        with open(self._output_tsv_file_name, 'w') as o_f, open(self._output_hi_conf_tsv_file_name, 'w') as o_hi_conf_f:

            # write header to the output tsv file
            output_header = '\t'.join([x for x in output_tsv_file_columns]) + '\n'
            o_f.write(output_header)
            o_hi_conf_f.write(output_header)

            row_count = 1
            row_count_hi_conf = 1

            with open(self._full_file_name, 'r') as f_f:
                next(f_f)
                for line in f_f:
                    columns_in_row = line.split(' ');
                    protein1, protein2 = columns_in_row[0], columns_in_row[1]

                    name_rep_alias_1 = self._get_name_rep_alias(protein1, ensembl_ids)
                    name_rep_alias_2 = self._get_name_rep_alias(protein2, ensembl_ids)

                    full_tsv_string = name_rep_alias_1 + '\t' + name_rep_alias_2 + '\t' + \
                                      '\t'.join(x for x in columns_in_row[2:])



                    o_f.write(full_tsv_string)
                    row_count = row_count + 1

                    combined_score = int(columns_in_row[-1].rstrip('\n'))
                    if combined_score > 700:
                        o_hi_conf_f.write(full_tsv_string)
                        row_count_hi_conf = row_count_hi_conf + 1

            print('Created {} ({:,} lines) and {} ({:,} lines) files\n'.\
                format(self._output_tsv_file_name, row_count, self._output_hi_conf_tsv_file_name, row_count_hi_conf))

        return 0


    def _generate_CX_file(self, file_name, network_name, network_id, template_id):
        template_network = ndex2.create_nice_cx_from_server(server=self._server,
                                                            uuid=template_id,
                                                            username=self._user,
                                                            password=self._pass)
        new_cx_file = file_name + '.cx'

        print('{} - generating CX file for network {}...'.format(str(datetime.now()), network_name))

        with open(file_name, 'r') as tsvfile:

            with open(new_cx_file, "w") as out:
                loader = StreamTSVLoader(self._load_plan, template_network)

                loader.write_cx_network(tsvfile, out,
                    [
                        {'n': 'name', 'v': network_name},
                        {'n': 'description', 'v': template_network.get_network_attribute('description')['v']},
                        {'n': 'rights', 'v': template_network.get_network_attribute('rights')['v']},
                        {'n': 'rightsHolder', 'v': template_network.get_network_attribute('rightsHolder')['v']},
                        {'n': 'version', 'v': self._string_version},
                        {'n': 'organism', 'v': template_network.get_network_attribute('organism')['v']},
                        {'n': 'networkType', 'v': template_network.get_network_attribute('networkType')['v']},
                        {'n': 'reference', 'v': template_network.get_network_attribute('reference')['v']},
                    ])

        print('{} - CX file for network {} generated\n'.format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), network_name))
        return new_cx_file


    def _update_network_on_server(self, new_cx_file, network_name, network_id):

        print('{} - updating network {} on server {} for user {}...'.format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                                                            network_name, self._server, self._user))

        with open(new_cx_file, 'br') as network_out:

            my_client = ndex2.client.Ndex2(host=self._server, username=self._user, password=self._pass)

            try:
                my_client.update_cx_network(network_out, network_id)
            except Exception as e:
                print('{} - server returned error: {}\n'.format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), e))
            else:
                print('{} - network {} updated on server {} for user {}\n'.format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                                                          network_name, self._server, self._user))
        return


    def load_to_NDEx(self):

        file_name = self._output_hi_conf_tsv_file_name
        network_name = "STRING - Human Protein Links - High Confidence (Score > 0.7)"
        network_id = self._hi_conf_network_id
        template_id = self._hi_conf_template_id

        cx_file_name = self._generate_CX_file(file_name, network_name, network_id, template_id)
        self._update_network_on_server(cx_file_name, network_name, network_id)


        file_name = self._output_tsv_file_name
        network_name = "STRING - Human Protein Links"
        network_id = self._network_id
        template_id = self._template_id

        cx_file_name = self._generate_CX_file(file_name, network_name, network_id, template_id)
        self._update_network_on_server(cx_file_name, network_name, network_id)


def main(args):
    """
    Main entry point for program
    :param args:
    :return:
    """
    desc = """
    Version {version}

    Loads NDEx STRING Content Loader data into NDEx (http://ndexbio.org).

    To connect to NDEx server a configuration file must be passed
    into --conf parameter. If --conf is unset, the configuration
    ~/{confname} is examined.

    The configuration file should be formatted as follows:

    [<value in --profile (default dev)>]

    {user} = <NDEx username>
    {password} = <NDEx password>
    {server} = <NDEx server(omit http) ie public.ndexbio.org>


    """.format(confname=NDExUtilConfig.CONFIG_FILE,
               user=NDExUtilConfig.USER,
               password=NDExUtilConfig.PASSWORD,
               server=NDExUtilConfig.SERVER,
               version=ndexstringloader.__version__)
    theargs = _parse_arguments(desc, args[1:])
    theargs.program = args[0]
    theargs.version = ndexstringloader.__version__

    try:
        _setup_logging(theargs)
        loader = NDExNdexstringloaderLoader(theargs)
        loader.run()
        loader.load_to_NDEx()
        return 0

    except Exception as e:
        print('\n   {} {}\n'.format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), e))
        logger.exception('Caught exception')
        return 2
    finally:
        logging.shutdown()


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
