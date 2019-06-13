from __future__ import print_function

import os
from graphviz import Digraph
from deriva.utils.catalog.components.deriva_model import DerivaCatalog

class DerivaCatalogToGraph:
    def __init__(self, catalog):
        self.graph = Digraph(
            engine='neato',
            format='pdf',
            edge_attr=None,
            strict=True)

        self.catalog = catalog
        self.graph.attr('graph', rankdir='LR')
        self.graph.attr('graph', overlap='false', splines='true')

    def catalog_to_graph(self, schemas=None, skip_terms=False, skip_assocation_tables=False):
        """
        Convert a catalog to a DOT based graph.
        :param schemas:  List of schemas that should be included.  Use whole catalog if None.
        :param skip_terms: Do not include term tables in the graph
        :param skip_assocation_tables: Collapse association tables so that only edges between endpoints are used
        :return:
        """

        schemas = [s for s in self.catalog.schemas if s not in ['_acl_admin', 'Public', 'WWW']] \
            if schemas is None else schemas

        for schema in schemas:
            self.schema_to_graph(schema, skip_terms=skip_terms, schemas=schemas,
                                 skip_assocation_tables=skip_assocation_tables)

    def schema_to_graph(self, schema_name, schemas=[], skip_terms=False, skip_assocation_tables=False):
        """
        Create a graph for the specified schema.
        :param schema_name: Name of the schema in the model to be used.
        :param schemas: List of additional schemas to include in the graph.
        :param skip_terms:
        :param skip_assocation_tables:
        :return:
        """
        schema = self.catalog.schemas[schema_name]

        # Put nodes for each schema in a seperate subgraph.
        with self.graph.subgraph(name=schema_name, node_attr={'shape': 'box'}) as schema_graph:
            for table in schema.tables:
                node_name = '{}_{}'.format(schema_name, table.name)

                if table.is_vocabulary_table():
                    if not skip_terms:
                        schema_graph.node(node_name, label='{}:{}'.format(schema_name, table.name), shape='ellipse')
                else:
                    # Skip over current table if it is a association table and option is set.
                    if not (table.is_pure_binary() and skip_assocation_tables):
                        schema_graph.node(node_name, label='{}:{}'.format(schema_name, table.name), shape='box')
                    else:
                        print('Skipping node', node_name)

        # We have all the nodes out now, so run over and add edges.
        for table in schema.tables:
            self.foreign_key_defs_to_graph(table,
                                           skip_terms=skip_terms,
                                           schemas=schemas,
                                           skip_association_tables=skip_assocation_tables)
        return

    def foreign_key_defs_to_graph(self, table, skip_terms=False, skip_association_tables=False, schemas=[]):
        """
        Add edges for each foreign key relationship in the specified table.
        :param table:
        :param skip_terms:
        :param skip_association_tables:
        :param skip_schemas:
        :return:
        """

        # If table is an association table, put in a edge between the two endpoints in the relation.
        if table.is_pure_binary() and skip_association_tables:
            [t1, t2] = table.associated_tables()
            t1_name = '{}_{}'.format(t1.schema_name, t1.name)
            t2_name = '{}_{}'.format(t2.schema_name, t2.name)
            self.graph.edge(t1_name, t2_name, dir='both', color='gray')
        else:
            for fkey in table.foreign_keys:
                table_name = '{}_{}'.format(fkey.referenced_table.schema_name,
                                            fkey.referenced_table.name)

                # If the target is a schema we are skipping, do not add an edge.
                if (fkey.referenced_table.schema_name not in schemas or table.schema_name not in schemas):
                    continue
                # If the target is a term table, and we are not including terms, do not add an edge.
                if fkey.referenced_table.is_vocabulary_table() and skip_terms:
                    continue

                # Add an edge from the current node to the target table.
                self.graph.edge('{}_{}'.format(table.schema_name, table.name), table_name)
        return

    def save(self, filename=None, format='pdf', view=False):
        (dir, file) = os.path.split(os.path.abspath(filename))
        if 'gv' in format:
            self.graph.save(filename=file, directory=dir)
        else:
            print('dumping graph in file', file, format)
            self.graph.render(filename=file, directory=dir, view=view, cleanup=True, format=format)

    def view(self):
        self.graph.view()
