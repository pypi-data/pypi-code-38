#! /usr/bin/env python

import argparse
import sys

from ndexutil.config import NDExUtilConfig
import ndexstringloader

from datetime import datetime

import ndex2




LOG_FORMAT = "%(asctime)-15s %(levelname)s %(relativeCreated)dms " \
             "%(filename)s::%(funcName)s():%(lineno)d %(message)s"

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
                                          'file that specifies user name, password, server network_id to be updated '
                                          ' and cx file name whose content will udate network with network_id '
                                          'NDEx credentials which means'
                                          'configuration under [XXX] will be'
                                          'used ', required=True)

    parser.add_argument('--conf', help='Configuration file to load '
                                       '(default ~/' +
                                       NDExUtilConfig.CONFIG_FILE)

    return parser.parse_args(args)


class NDExUpdateNetwork(object):
    """
    Class to update content
    """
    def __init__(self, args):
        """
        :param args:
        """
        self._conf_file = args.conf
        self._profile = args.profile

        #self._network_id = args.networkid
        #self._update_cx_file_name = args.cx


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
        self._network_id = con.get(self._profile, 'network_id')
        self._update_cx_file_name = con.get(self._profile, 'update_cx_file_name')

        ret_value = 0
        if not self._user:
            print('user is not specified in configuration file')
            ret_value = 2

        if not self._pass:
            print('password is not specified in configuration file')
            ret_value = 2

        if not self._server:
            print('server is not specified in configuration file')
            ret_value = 2

        if not self._network_id:
            print('network_id is not specified in configuration file')
            ret_value = 2

        if not self._update_cx_file_name:
            print('update_cx_file_name is not specified in configuration file')
            ret_value = 2

        return ret_value

        #if not self._network_id:
        #    self._network_id = con.get(self._profile, 'network_id')

        #if not self._update_cx_file_name:
        #    self._update_cx_file_name = con.get(self._profile, 'update_cx_file_name')



    def _update_network_on_server(self):

        print('{} - updating network {} from cx file {} on server {} for user {}...'
              .format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                  self._network_id, self._update_cx_file_name, self._server, self._user))

        with open(self._update_cx_file_name, 'br') as network_out:

            my_client = ndex2.client.Ndex2(host=self._server, username=self._user, password=self._pass)

            try:
                my_client.update_cx_network(network_out, self._network_id)
            except Exception as e:
                print('{} - server returned error: {}\n'.format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), e))
                return 2
            else:
                print('{} - updated network {} from cx file {} on server {} for user {}'
                      .format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                              self._network_id, self._update_cx_file_name, self._server, self._user))

        return 0



    def run(self):
        status_code = self._parse_config()

        if status_code == 0:
            status_code = self._update_network_on_server()

        return status_code



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
    into --conf parameter. If --conf is unset the configuration
    the path ~/{confname} is examined.

    The configuration file should be formatted as follows:

    [<value in --profile (default ndex_update)>]

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
        updater = NDExUpdateNetwork(theargs)
        updater.run()
        return 0

    except Exception as e:
        print('\n   {} {}\n'.format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), e))
        return 2

    finally:
        pass


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
