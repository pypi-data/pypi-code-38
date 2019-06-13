from __future__ import print_function

import argparse
import ast
import logging
import os
import re
import sys
import traceback
import requests
from requests.exceptions import HTTPError, ConnectionError

from deriva.core import format_exception
from deriva.core.utils import eprint
from deriva.core.base_cli import BaseCLI

from yapf.yapflib.yapf_api import FormatCode

from deriva.core import get_credential, AttrDict

from deriva.core.ermrest_config import tag as chaise_tags
from deriva.utils.catalog.manage.deriva_file_templates import table_file_template, schema_file_template, \
    catalog_file_template
from deriva.utils.catalog.components.deriva_model import DerivaCatalog, DerivaModel

from deriva.utils.catalog.version import __version__ as VERSION
from deriva.utils.catalog.manage.graph_catalog import DerivaCatalogToGraph

IS_PY2 = (sys.version_info[0] == 2)
IS_PY3 = (sys.version_info[0] == 3)


from urllib.parse import urlparse


logger = logging.getLogger(__name__)

yapf_style = {
    'based_on_style': 'pep8',
    'allow_split_before_dict_value': False,
    'split_before_first_argument': False,
    'disable_ending_comma_heuristic': True,
    'DEDENT_CLOSING_BRACKETS': True,
    'column_limit': 100
}


class DerivaDumpCatalogException (Exception):
    """Base exception class for DerivaDumpCatalog.
    """
    def __init__(self, message):
        """Initializes the exception.
        """
        super(DerivaDumpCatalogException, self).__init__(message)


class UsageException (DerivaDumpCatalogException):
    """Usage exception.
    """
    def __init__(self, message):
        """Initializes the exception.
        """
        super(UsageException, self).__init__(message)


class DerivaCatalogToString:
    def __init__(self, catalog, provide_system_columns=True, groups=None):
        self._catalog = catalog
        self._provide_system_columns = provide_system_columns
        # Get the currently known groups for this catalog.
        self._groups = groups
        if groups is None:
            try:
                self._groups = AttrDict(
                    {e['Display_Name']: e['ID'] for e in catalog.getPathBuilder().public.ERMrest_Group.entities()}
                )
            except AttributeError:
                logger.warning('Cannot access ERMrest_Group table. Check ACLs')
                self._groups = AttrDict()

        self._referenced_groups = {}
        self._variables = self._groups.copy()
        self._variables.update(chaise_tags)

    def substitute_variables(self, code):
        """
        Factor out code and replace with a variable name.
        :param code:
        :return: new code
        """
        for k, v in self._variables.items():
            varsub = r"(['\"])+{}\1".format(v)
            if k in chaise_tags:
                repl = 'chaise_tags.{}'.format(k)
            elif k in self._groups:
                repl = 'groups[{!r}]'.format(k)
                if v in code:
                    self._referenced_groups[k] = v
            else:
                repl = k
            code = re.sub(varsub, repl, code)

        return code

    def variable_to_str(self, name, value, substitute=True):
        """
        Print out a variable assignment on one line if empty, otherwise pretty print.
        :param name: Left hand side of assigment
        :param value: Right hand side of assignment
        :param substitute: If true, replace the group and tag values with their corresponding names
        :return:
        """

        s = '{} = {!r}\n'.format(name, value)
        if substitute:
            s = self.substitute_variables(s)
        return s

    def tag_variables_to_str(self, annotations):
        """
        For each convenient annotation name in tag_map, print out a variable declaration of the form annotation = v
        where v is the value of the annotation the dictionary.  If the tag is not in the set of annotations, do nothing.
        :param annotations:
        :return:
        """
        s = []
        for t, v in chaise_tags.items():
            if v in annotations:
                s.append(self.variable_to_str(t, annotations[v]))
                s.append('\n')
        return ''.join(s)

    def annotations_to_str(self, annotations, var_name='annotations'):
        """
        Print out the annotation definition in annotations, substituting the python variable for each of the tags
        specified in tag_map.
        :param annotations:
        :param var_name:
        :return:
        """

        var_map = {v: k for k, v in self._variables.items()}
        if annotations == {}:
            s = '{} = {{}}\n'.format(var_name)
        else:
            s = '{} = {{'.format(var_name)
            for t, v in annotations.items():
                if t in var_map:
                    # Use variable value rather then inline annotation value.
                    s += self.substitute_variables('{!r}:{},'.format(t, var_map[t]))
                else:
                    s += "'{}' : {!r},".format(t, v)
            s += '}\n'
        return s

    def schema_to_str(self, schema_name):
        schema = self._catalog[schema_name]
        host = self._catalog.host
        catalog_id = self._catalog.catalog_id

        annotations = self.variable_to_str('annotations', schema.annotations)
        acls = self.variable_to_str('acls', schema.acls.value)
        comments = self.variable_to_str('comment', schema.comment)
        groups = self.variable_to_str('groups', self._referenced_groups, substitute=False)

        s = schema_file_template.format(host=host, catalog_id=catalog_id, schema_name=schema_name,
                                        annotations=annotations, acls=acls, comments=comments, groups=groups,
                                        table_names='table_names = [\n{}]\n'.format(
                                            str.join('', ['{!r},\n'.format(i.name) for i in schema.tables])))
        s = FormatCode(s, style_config=yapf_style)[0]
        return s

    def catalog_to_str(self):
        host = self._catalog.host
        catalog_id = self._catalog.catalog_id

        tag_variables = self.tag_variables_to_str(self._catalog.annotations)
        annotations = self.annotations_to_str(self._catalog.annotations)
        acls = self.variable_to_str('acls', self._catalog.acls.value)
        groups = self.variable_to_str('groups', self._referenced_groups, substitute=False)

        s = catalog_file_template.format(host=host, catalog_id=catalog_id, groups=groups,
                                         tag_variables=tag_variables,
                                         annotations=annotations,
                                         acls=acls)
        s = FormatCode(s, style_config=yapf_style)[0]
        return s

    def table_annotations_to_str(self, table):
        s = ''.join([self.tag_variables_to_str(table.annotations), '\n',
                     self.annotations_to_str(table.annotations, var_name='table_annotations'), '\n',
                     self.variable_to_str('table_comment', table.comment), '\n',
                     self.variable_to_str('table_acls', table.acls.value), '\n',
                     self.variable_to_str('table_acl_bindings', table.acl_bindings.value)])
        return s

    def column_annotations_to_str(self, table):
        column_annotations = {}
        column_acls = {}
        column_acl_bindings = {}
        column_comment = {}

        for i in table.columns:
            if not (i.annotations == '' or not i.comment):
                column_annotations[i.name] = i.annotations
            if not (i.comment == '' or not i.comment):
                column_comment[i.name] = i.comment
            if i.annotations != {}:
                column_annotations[i.name] = i.annotations
            if i.acls != {}:
                column_acls[i.name] = i.acls
            if i.acl_bindings != {}:
                column_acl_bindings[i.name] = i.acl_bindings
        s = self.variable_to_str('column_annotations', column_annotations) + '\n'
        s += self.variable_to_str('column_comment', column_comment) + '\n'
        s += self.variable_to_str('column_acls', column_acls) + '\n'
        s += self.variable_to_str('column_acl_bindings', column_acl_bindings) + '\n'
        return s

    def foreign_key_defs_to_str(self, table):
        s = 'fkey_defs = [\n'
        for fkey in table.foreign_keys:
            s += """    em.ForeignKey.define({},
                '{}', '{}', {},
                constraint_names={},\n""".format([c.name for c in fkey.columns],
                                                 fkey.referenced_table.schema_name,
                                                 fkey.referenced_table.name,
                                                 [c.name for c in fkey.referenced_columns],
                                                 [fkey.full_name])

            for i in ['annotations', 'acls', 'acl_bindings', 'on_update', 'on_delete', 'comment']:
                a = getattr(fkey, i)
                if not (a == {} or a is None or a == 'NO ACTION' or a == ''):
                    v = "'" + a + "'" if re.match('comment|on_update|on_delete', i) else a
                    s += "        {}={},\n".format(i, v)
            s += '    ),\n'

        s += ']'
        s = self.substitute_variables(s)
        return s

    def key_defs_to_str(self, table):
        s = 'key_defs = [\n'
        for key in table.keys:
            s += """    em.Key.define({},
                       constraint_names={},\n""".format([c.name for c in key.columns],
                                                        [key.full_name] if key.name else [])
            for i in ['annotations', 'comment']:
                a = getattr(key, i)
                if not (a == {} or a is None or a == ''):
                    v = "'" + a + "'" if i == 'comment' else a
                    s += "       {} = {},\n".format(i, v)
            s += '),\n'
        s += ']'
        s = self.substitute_variables(s)
        return s

    def column_defs_to_str(self, table):
        system_columns = ['RID', 'RCB', 'RMB', 'RCT', 'RMT']

        s = ['column_defs = [']
        for col in table.columns:
            if col.name in system_columns and self._provide_system_columns:
                continue
            s.append('''    em.Column.define('{}', em.builtin_types['{}'],'''.
                     format(col.name, col.type.typename + '[]' if 'is_array' is True else col.type.typename))
            if col.nullok is False:
                s.append("nullok=False,")
            if col.default and col.name not in system_columns:
                s.append("default={!r},".format(col.default))
            for i in ['annotations', 'acls', 'acl_bindings', 'comment']:
                colvar = getattr(col, i)
                if colvar:  # if we have a value for this field....
                    s.append("{}=column_{}['{}'],".format(i, i, col.name))
            s.append('),\n')
        s.append(']')
        return ''.join(s)

    def table_def_to_str(self):
        s = """table_def = em.Table.define(table_name,
        column_defs=column_defs,
        key_defs=key_defs,
        fkey_defs=fkey_defs,
        annotations=table_annotations,
        acls=table_acls,
        acl_bindings=table_acl_bindings,
        comment=table_comment,
        provide_system = {}
    )""".format(self._provide_system_columns)
        return s

    def table_to_str(self, schema_name, table_name):
        logger.debug('%s %s %s', schema_name, table_name, [i.name for i in self._catalog.schemas])
        table = self._catalog[schema_name][table_name]

        host = self._catalog.host
        catalog_id = self._catalog.catalog_id

        column_annotations = self.column_annotations_to_str(table)
        column_defs = self.column_defs_to_str(table)
        table_annotations = self.table_annotations_to_str(table)
        key_defs = self.key_defs_to_str(table)
        fkey_defs = self.foreign_key_defs_to_str(table)
        table_def = self.table_def_to_str()
        groups = self.variable_to_str('groups', self._referenced_groups, substitute=False)

        s = table_file_template.format(host=host, catalog_id=catalog_id,
                                       table_name=table_name, schema_name=schema_name, groups=groups,
                                       column_annotations=column_annotations,
                                       column_defs=column_defs,
                                       table_annotations=table_annotations,
                                       key_defs=key_defs,
                                       fkey_defs=fkey_defs,
                                       table_def=table_def)
        s = FormatCode(s, style_config=yapf_style)[0]
        return s


class DerivaDumpCatalogCLI (BaseCLI):

    def __init__(self, description, epilog):
        super(DerivaDumpCatalogCLI, self).__init__(description, epilog, VERSION, hostname_required=True)

        def python_value(s):
            try:
                val = ast.literal_eval(s)
            except ValueError:
                val = s
            return val

        self.dumpdir = ''
        self.host = None
        self.catalog_id = 1
        self.graph_format = None
        self.catalog = None

        # parent arg parser
        parser = self.parser
        parser.add_argument('--catalog', '--catalog-id', metavar='CATALOG-NUMBER', default=1, help='ID number of desired catalog')
        parser.add_argument('--dir', default="catalog-configs", help='output directory name')
        parser.add_argument('--table', default=None, help='Only dump out the spec for the specified table.  Format is '
                                                          'schema_name:table_name')
        parser.add_argument('--schemas', nargs='*', default=[],
                            help='Only dump out the spec for the specified schemas.')
        parser.add_argument('--skip-schemas', nargs='*', default=[], help='List of schema so skip over')
        parser.add_argument('--graph', action='store_true', help='Dump graph of catalog')
        parser.add_argument('--graph-format', choices=['pdf', 'dot', 'png', 'svg'],
                            default='pdf', help='Format to use for graph dump')

    @staticmethod
    def _get_credential(host_name, token=None):
        if token:
            return {"cookie": "webauthn={t}".format(t=token)}
        else:
            return get_credential(host_name)

    def _dump_table(self, schema_name, table_name, stringer=None, dumpdir='.'):
        logger.info("Dumping out  table def: {}:{}".format(schema_name,table_name))
        if not stringer:
            stringer = DerivaCatalogToString(self.catalog)

        table_string = stringer.table_to_str(schema_name, table_name)
        filename= dumpdir + '/' + table_name + '.py'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            print(table_string, file=f)

    def _dump_catalog(self, model):
        stringer = DerivaCatalogToString(self.catalog)
        catalog_string = stringer.catalog_to_str()

        with open('{}/{}_{}.py'.format(self.dumpdir, self.host, self.catalog_id), 'w') as f:
            print(catalog_string, file=f)

        for schema_name in self.schemas:
            logger.info("Dumping schema def for {}....".format(schema_name))
            schema_string = stringer.schema_to_str(schema_name)

            with open('{}/{}.schema.py'.format(self.dumpdir, schema_name), 'w') as f:
                print(schema_string, file=f)

        for schema_name, schema in model.schemas.items():
            for table_name in schema.tables:
                self._dump_table(schema_name, table_name, stringer=stringer,
                                 dumpdir='{}/{}'.format(self.dumpdir, schema_name))

    def _graph_catalog(self):
        graph = DerivaCatalogToGraph(self.catalog)
        graphfile = '{}_{}'.format(self.host, self.catalog_id)
        graph.catalog_to_graph(schemas=[s for s in self.schemas if s not in ['_acl_admin', 'public', 'WWW']],
                               skip_terms=True,
                               skip_assocation_tables=True)
        graph.save(filename=graphfile, format=self.graph_format)

    def main(self):
        args = self.parse_cli()

        self.dumpdir = args.dir
        self.host = args.host
        self.catalog_id = args.catalog
        self.graph_format = args.graph_format

        if self.host is None:
            eprint('Host name must be provided')
            return 1

        self.catalog = DerivaCatalog(self.host, catalog_id=self.catalog_id, validate=False)

        with DerivaModel(self.catalog) as m:
            model_root = m.catalog_model()

            self.schemas = [s for s in (args.schemas if args.schemas else model_root.schemas)
                            if s not in args.skip_schemas
                            ]

            try:
                os.makedirs(self.dumpdir, exist_ok=True)
            except OSError as e:
                sys.stderr.write(str(e))
                return 1

            logger.info('Catalog has {} schema and {} tables'.format(len(model_root.schemas),
                                                                     sum([len(v.tables) for k, v in
                                                                          model_root.schemas.items()])))
            logger.info('\n'.join(['    {} has {} tables'.format(k, len(s.tables))
                                   for k, s in model_root.schemas.items()]))
            try:
                if args.table:
                    if ':' not in args.table:
                        raise DerivaDumpCatalogException('Table name must be in form of schema:table')
                    [schema_name, table_name] = args.table_model.split(":")
                    self._dump_table(schema_name, table_name)
                elif args.graph:
                    self._graph_catalog()
                else:
                    self._dump_catalog(model_root)
            except DerivaDumpCatalogException as e:
                print(e.msg)
            except HTTPError as e:
                if e.response.status_code == requests.codes.unauthorized:
                    msg = 'Authentication required for {}'.format(args.server)
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
    DESC = "DERIVA Dump Catalog Command-Line Interface"
    INFO = "For more information see: https://github.com/informatics-isi-edu/deriva-catalog-manage"
    return DerivaDumpCatalogCLI(DESC, INFO).main()


if __name__ == '__main__':
    sys.exit(main())
