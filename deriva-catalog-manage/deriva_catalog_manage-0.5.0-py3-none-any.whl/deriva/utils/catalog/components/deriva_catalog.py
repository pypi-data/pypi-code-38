import argparse
import sys
import warnings
import logging
from requests import exceptions
import traceback
import requests
from requests.exceptions import HTTPError, ConnectionError
from urllib.parse import urlparse

import deriva.core.ermrest_model as em
from deriva.core.ermrest_config import tag as chaise_tags
from deriva.core import ErmrestCatalog, get_credential, format_exception
from deriva.core.utils import eprint
from deriva.core.base_cli import BaseCLI
from deriva.utils.catalog.components.deriva_model import DerivaModel, DerivaCatalog, DerivaSchema, \
    DerivaTable, DerivaContext
from deriva.utils.catalog.components.configure_catalog import DerivaTable
from deriva.utils.catalog.version import __version__ as VERSION

logger = logging.getLogger(__name__)

chaise_tags.catalog_config = 'tag:isrd.isi.edu,2019:catalog-config'


class DerivaModelElementsCLI(BaseCLI):

    def __init__(self, description, epilog):
        """Initializes the CLI.
        """
        super(DerivaModelElementsCLI, self).__init__(description, epilog, VERSION, hostname_required=True)

        # initialized after argument parsing
        self.args = None
        self.host = None

        # parent arg parser
        parser = self.parser


class DerivaConfigureCatalogCLI(BaseCLI):

    def __init__(self, description, epilog):
        super(DerivaConfigureCatalogCLI, self).__init__(description, epilog, VERSION, hostname_required=True)

        # parent arg parser
        parser = self.parser
        parser.add_argument('configure', choices=['catalog', 'table'],
                            help='Choose between configuring a catalog or a specific table')
        parser.add_argument('--catalog-name', default=None, help="Name of catalog (Default:hostname)")
        parser.add_argument('--catalog', default=1, help="ID number of desired catalog (Default:1)")
        parser.add_argument('--table', default=None, metavar='SCHEMA_NAME:TABLE_NAME',
                            help='Name of table to be configured')
        parser.add_argument('--set-policy', default='True', choices=[True, False],
                            help='Access control policy to be applied to catalog or table')
        parser.add_argument('--reader-group', dest='reader', default=None,
                            help='Group name to use for readers. For a catalog named "foo" defaults for foo-reader')
        parser.add_argument('--writer-group', dest='writer', default=None,
                            help='Group name to use for writers. For a catalog named "foo" defaults for foo-writer')
        parser.add_argument('--curator-group', dest='curator', default=None,
                            help='Group name to use for readers. For a catalog named "foo" defaults for foo-curator')
        parser.add_argument('--admin-group', dest='admin', default=None,
                            help='Group name to use for readers. For a catalog named "foo" defaults for foo-admin')
        parser.add_argument('--publish', default=False, action='store_true',
                            help='Make the catalog or table accessible for reading without logging in')
        parser.add_argument('table', default=None, metavar='SCHEMA_NAME:TABLE_NAME',
                            help='Name of table to be configured')
        parser.add_argument('--asset-table', default=None, metavar='KEY_COLUMN',
                            help='Create an asset table linked to table on key_column')
        parser.add_argument('--visible-columns', action='store_true',
                            help='Create a default visible columns annotation')
        parser.add_argument('--replace', action='store_true', help='Overwrite existing value')

    @staticmethod
    def _get_credential(host_name, token=None):
        if token:
            return {"cookie": "webauthn={t}".format(t=token)}
        else:
            return get_credential(host_name)

    def main(self):

        args = self.parse_cli()

        catalog = DerivaCatalogConfigure(args.host, catalog_id=args.catalog_model)

        try:
            catalog = DerivaCatalog(args.host, args.catalog_model)
            [schema_name, table_name] = args.table_model.split(':')
            table = DerivaTable(catalog, schema_name, table_name)
            if args.asset_table:
                table.create_asset_table(args.asset_table)
            if args._visible_columns:
                table.create_default_visible_columns(really=args.replace)

            if args.configure == 'catalog':
                logging.info('Configuring catalog {}:{}'.format(args.host, args.catalog_model))
                cfg = DerivaCatalogConfigure(args.host, catalog_id=args.catalog_model)
                cfg.configure_baseline_catalog(catalog_name=args.catalog_name,
                                               reader=args.reader, writer=args.writer, curator=args.curator,
                                               admin=args.admin,
                                               set_policy=args.set_policy, public=args.publish)
                cfg.apply()
            if args.table_model:
                [schema_name, table_name] = args.table_model.split(':')
                table = catalog.schema(schema_name).table_model(table_name)
                table.configure_table_defaults(set_policy=args.set_policy, public=args.publish)
                table.apply()
        except DerivaConfigError as e:
            print(e.msg)
        except HTTPError as e:
            if e.response.status_code == requests.codes.unauthorized:
                msg = 'Authentication required for {}'.format(args.host)
            elif e.response.status_code == requests.codes.forbidden:
                msg = 'Permission denied'
            else:
                msg = e
            logging.debug(format_exception(e))
            eprint(msg)
        except RuntimeError as e:
            sys.stderr.write(str(e))
            return 1
        except:
            traceback.print_exc()
            return 1
        finally:
            sys.stderr.write("\n\n")
        return


def main():
    DESC = "DERIVA Configure Catalog Command-Line Interface"
    INFO = "For more information see: https://github.com/informatics-isi-edu/deriva-catalog-manage"
    return DerivaConfigureCatalogCLI(DESC, INFO).main()


if __name__ == '__main__':
    sys.exit(main())
