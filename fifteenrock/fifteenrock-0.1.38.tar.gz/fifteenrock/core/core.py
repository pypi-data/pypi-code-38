# -*- coding: utf-8 -*-

"""Main module."""
import json
import requests
from typing import *
from fifteenrock.lib import util, helper
from pyrsistent import freeze, pvector
import os
from shutil import copyfile

# fr.deploy(name='EchoHandler',
#               handler=e,
#               url='https://www.15rock.com',
#               credentials={'u': 'r', 'p': 'pp'},
#               project='p1'
#               )
DEFAULT_COMPUTE_ENDPOINT = 'https://app.15rock.com/gateway/compute'
REQUIREMENTS_FILE = 'requirements.txt'


class BaseHandler(object):
    pass


def delete_function(project: str, function: str, url: str = None, credentials: Dict[str, str] = None,
                    credentials_file: str = None
                    ):
    # TODO: A lot of duplication with list_function etc.

    endpoint = 'function'
    raw_data = dict(project=project, function=function)
    error_message = "Error in Deleting function"

    credentials = helper.get_credentials(credentials, credentials_file)
    url = url or DEFAULT_COMPUTE_ENDPOINT
    endpoint_url = make_compute_url(url) + f'/{endpoint}'
    headers = make_credentials_header(credentials)
    new_headers = {**headers, **{"Content-type": "application/json"}}

    return util.delete(endpoint_url, raw_data=raw_data, headers=new_headers)


def list_functions(url: str = None, credentials: Dict[str, str] = None, credentials_file: str = None,
                   project: str = None, function: str = None):
    filters = dict()
    if project:
        filters['project_name'] = project
    if function:
        filters['function_name'] = function

    endpoint = 'function'
    raw_data = dict(filters=filters)
    error_message = "Error in Listing function"

    credentials = helper.get_credentials(credentials, credentials_file)
    url = url or DEFAULT_COMPUTE_ENDPOINT
    list_url = make_compute_url(url) + f'/{endpoint}'
    headers = make_credentials_header(credentials)
    new_headers = {**headers, **{"Content-type": "application/json"}}

    response = util.get_response(list_url, raw_data=raw_data, headers=new_headers)
    if response:
        return response.json()
    else:
        raise ValueError(error_message)


def deploy(project: str, function: str, url: str = None, main_file: str = None, dependencies: List = None,
           requirements_file: str = None, runtime: str = None, runtime_version: str = None, project_folder: str = None,
           credentials: Dict[str, str] = None, credentials_file: str = None, spec: Dict = None, metadata: Dict = None,
           config_file: str = None):
    """

    :param main_file:
    :param credentials:
    :param credentials_file: Path to the credentials file
    :param url:
    :param project:
    :param dependencies: files or folders not in your project_folder which you want to add to your deployment package.
        An example could be an external secrets file or some shared code outside your repo(which is not a pip
        library for e.g.)
    :param function:
    :param requirements_file:
    :param runtime:
    :param runtime_version:
    :param project_folder:
    :param spec: Dict of resources, image setup commands etc.
    :param metadata: Dict of labels, annotations etc.
    :param config_file: Config file. Any values passed in explicitly will override any values in the config file.
    Note, this pertains only to `spec` and `metadata` keys right now. i.e. if spec is provided, it will __completely__
    replace any values specified in the *config_file*
    :return:
    """

    tmp_folder = util.tmp_folder()

    credentials = helper.get_credentials(credentials, credentials_file)
    config = helper.read_config(config_file)
    url = url or DEFAULT_COMPUTE_ENDPOINT
    main_file = main_file or helper.default_file_path('main.py')
    util.required('main_file', main_file)
    util.fail_if_no_file(main_file)
    if requirements_file:
        # copy_file with name requirements.txt

        dst = str(tmp_folder / REQUIREMENTS_FILE)
        copyfile(requirements_file, dst)
        requirements_file = dst
    else:
        requirements_file = helper.default_file_path(REQUIREMENTS_FILE) or str(util.make_requirements_file(tmp_folder))

    # project_folder = project_folder or os.getcwd()

    # requirements_file = requirements_file or str(util.make_requirements_file(tmp_folder))
    # name = name or util.file_name(main_file)
    dependencies = make_dependencies(dependencies, main_file, project_folder, requirements_file)

    spec = spec or config.get('spec') or dict()
    metadata = metadata or config.get('metadata') or dict()
    runtime = runtime or 'python'
    runtime_version = runtime_version or '3.6'

    runtime_path = tmp_folder / 'runtime.txt'
    runtime_path.write_text(runtime + '-' + runtime_version)
    credentials_tmp_path = tmp_folder / helper.FR_FILE_NAME
    dependencies = dependencies.append(str(runtime_path))

    util.write_credentials(credentials_tmp_path, credentials)
    dependencies = dependencies.append(str(credentials_tmp_path))
    # project_folder = project_folder or util.determine_project_folder()

    # dependencies = dependencies.extend([fifteenrock])

    # dependency_paths = [util.module_path(d) for d in dependencies]

    dependency_paths = pvector(util.module_path(d) for d in dependencies)

    optional = util.optional(project=project, name=function, spec=spec, metadata=metadata)
    mandatory = dict(credentials=credentials, main_file_name=os.path.basename(main_file))
    raw_data = {**mandatory, **optional}
    compute_url = make_compute_url(url)
    deploy_url = compute_url + '/deploy'

    archive_file = tmp_folder / 'archive.zip'

    util.archive(archive_file, dependency_paths)

    headers = make_credentials_header(credentials)
    try:
        deploy_result = deploy_to_compute(archive_file, headers, deploy_url, raw_data)
        poll_result = poll_if_function_created(deploy_result['function_id'], compute_url, headers)
        return dict(message=[f"Function available at {poll_result['function_url']}"])
    except Exception as e:
        raise e
    finally:
        util.remove_dir(tmp_folder)


def make_credentials_header(credentials):
    return dict(apikey=credentials['faas_token'])


def make_compute_url(url):
    compute_url = url + '/api/v0'
    return compute_url


def make_dependencies(dependencies, main_file, project_folder, requirements_file):
    dependencies = dependencies or []
    dependencies = freeze(dependencies)
    dependencies = dependencies.append(main_file)
    dependencies = dependencies.append(requirements_file)
    if project_folder:
        dependencies = dependencies.append(project_folder)
    return dependencies


# def poll_if_function_created(function_id, compute_url: str, headers: Dict):
#     tries = range(60)
#     interval = 30
#
#     import time
#
#     raw_data = dict(function_id=function_id)
#     status_url = compute_url + '/function_status'
#     new_headers = {**headers, **{"Content-type": "application/json"}}
#     for i in tries:
#         print(f'Try:{i}')
#         result = util.get_json(status_url, raw_data=raw_data, headers=new_headers)
#         code = result['code']
#         if code == 200:
#             return result
#         elif code == 40:
#             raise ValueError('Error in creating function')
#         # if code == 400:
#         #     # TODO: Report actual error
#         #     raise ValueError('Error in creating function')
#         # elif code == 200:
#         #     return result
#         time.sleep(interval)
#
#     # Else raise Timeout error
#     raise ValueError('Function creation timed out. Please try again.')

def poll_if_function_created(function_id, compute_url: str, headers: Dict):
    tries = range(60)
    interval = 30

    import time

    raw_data = dict(function_id=function_id)
    status_url = compute_url + '/function_status'
    new_headers = {**headers, **{"Content-type": "application/json"}}
    for i in tries:
        response = util.get_response(status_url, raw_data=raw_data, headers=new_headers)
        if response:
            result = response.json()
            code = result['code']
            if code == 200:
                return result
        else:
            raise ValueError('Error in creating function')

        time.sleep(interval)

    # Else raise Timeout error
    raise ValueError('Function creation timed out. Please try again.')


def deploy_to_compute(archive_file, headers, new_url, raw_data):
    return util.post(new_url, raw_data=raw_data, files={'archive': archive_file}, headers=headers)


# class DatabaseClient(object):
#     def __init__(self, url: str, credentials: Dict):
#         # self._url = url
#         self._url = url + '/' + 'v0'
#         self.credentials = credentials
#         pass
#
#     def url(self):
#         return self._url
#
#     # def drop(self, schema, table):
#     #     drop_query = f"DROP TABLE IF EXISTS {schema}.{table};"
#     #
#     #     self.execute_command(command=drop_query)
#
#     def query_sql(self, query: str):
#         raw_data = dict(credentials=self.credentials, query=query)
#         return self.post_json('/query_sql', raw_data)
#
#         # return result.json()
#
#     def post_json(self, url_part: str, raw_data: Dict):
#
#         headers = {"Content-type": "application/json"}
#
#         a_url = self.url() + url_part
#         try:
#             result = requests.post(a_url, headers=headers, data=json.dumps(raw_data))
#             js = result.json()
#             result.raise_for_status()
#             return js
#
#         except requests.exceptions.RequestException as e:
#             print(f"ROCK_ERROR:{json.dumps(js)}")
#             raise e
#
#     def execute_command(self, command: str):
#         result = self.post_json('/execute_command', dict(credentials=self.credentials, query=command))
#         # TODO: Start of GRAPHQL Code. Commenting for now
#         # tables = get_tables_to_track(query)
#         #
#         # for t in tables:
#         #
#         #     schema = t[0]
#         #     self.query_hasura([track_table(schema, t[1])])
#         #     table_info = self.query_hasura_single(get_table_info_for_relationships(schema))
#         #     if table_info:
#         #         fkc_dicts = get_foreign_key_constraints(table_info)
#         #         for fkc in fkc_dicts:
#         #             rel = get_object_relationship(fkc)
#         #             obj_rel_cmd = create_object_relationship(rel['label'], rel['schema'], rel['table_name'],
#         #                                                      rel['foreign_key'])
#         #             self.query_hasura_single(obj_rel_cmd)
#         #         for fkc in fkc_dicts:
#         #             rel = get_array_relationship(fkc)
#         #             arr_rel_cmd = create_array_relationship(rel['label'], rel['ref_schema'], rel['ref_table'],
#         #                                                     rel['schema'], rel['table_name'], rel['foreign_key'])
#         #             self.query_hasura_single(arr_rel_cmd)
#         # TODO: End of GRAPHQL Code. Commenting for now
#         return result
#
#     @staticmethod
#     def insert_query(table_name: str, columns: List, values: List):
#         cn = ', '.join(columns)
#         vn = []
#         for v in values:
#             if type(v) != str:
#                 vx = str(v)
#             else:
#                 vx = "'" + v + "'"
#             vn.append(vx)
#         vn = ', '.join(vn)
#         return f"INSERT INTO {table_name} ({cn}) VALUES ({vn});"
#
#     def insert_sql(self, table, columns, values):
#         inserts = [self.insert_query(table, columns, vn) for vn in values]
#         self.execute_command(command=''.join(inserts))
#
#     # def read(self, columns: List[str]):
#     #
#     #     return self.post_json('/read', dict(credentials=self.credentials, columns=json.dumps(columns)))
#
#     # def query_graphl(self, query: str):
#     #     request = requests.post(self.url() + "/graphql", json={'query': query})
#     #     if request.status_code == 200:
#     #         result = request.json()
#     #     else:
#     #         raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))
#     #
#     #     return result
#
#     # def query_graphl(self, query: str):
#     #     return self.post_json('/graphql', dict(query=query))
#     #
#     # def query_hasura(self, query_dict: List[Dict]):
#     #     result = []
#     #     for q in query_dict:
#     #         r = self.post_json('/hasura_api', dict(query=q))
#     #         result.append(r)
#     #     return result
#     #
#     # def query_hasura_single(self, query_dict: Dict):
#     #     return self.post_json('/hasura_api', dict(query=query_dict))
#


class DatabaseClient(object):
    def __init__(self, url: str, credentials: Dict):
        # self._url = url
        # self._url = url + '/' + 'v0'
        self._url = url + "/api/v0/db"
        self.credentials = credentials
        pass

    def url(self):
        return self._url

    # def drop(self, schema, table):
    #     drop_query = f"DROP TABLE IF EXISTS {schema}.{table};"
    #
    #     self.execute_command(command=drop_query)

    def query_sql(self, query: str):
        raw_data = dict(credentials=self.credentials, query=query)
        return self.post_json('/query_sql', raw_data)

        # return result.json()

    def post_json(self, url_part: str, raw_data: Dict):
        headers = {"Content-type": "application/json",
                   "apikey": self.credentials['faas_token']}

        a_url = self.url() + url_part
        try:

            result = requests.post(a_url, headers=headers, data=json.dumps(raw_data))
            js = result.json()
            result.raise_for_status()
            # js = util.post(a_url, raw_data=raw_data, headers=headers)
            return js

        except requests.exceptions.RequestException as e:
            print(f"ROCK_ERROR:{json.dumps(js)}")
            raise e

    def execute_command(self, command: str):
        result = self.post_json('/execute_command', dict(credentials=self.credentials, query=command))
        # TODO: Start of GRAPHQL Code. Commenting for now
        # tables = get_tables_to_track(query)
        #
        # for t in tables:
        #
        #     schema = t[0]
        #     self.query_hasura([track_table(schema, t[1])])
        #     table_info = self.query_hasura_single(get_table_info_for_relationships(schema))
        #     if table_info:
        #         fkc_dicts = get_foreign_key_constraints(table_info)
        #         for fkc in fkc_dicts:
        #             rel = get_object_relationship(fkc)
        #             obj_rel_cmd = create_object_relationship(rel['label'], rel['schema'], rel['table_name'],
        #                                                      rel['foreign_key'])
        #             self.query_hasura_single(obj_rel_cmd)
        #         for fkc in fkc_dicts:
        #             rel = get_array_relationship(fkc)
        #             arr_rel_cmd = create_array_relationship(rel['label'], rel['ref_schema'], rel['ref_table'],
        #                                                     rel['schema'], rel['table_name'], rel['foreign_key'])
        #             self.query_hasura_single(arr_rel_cmd)
        # TODO: End of GRAPHQL Code. Commenting for now
        return result

    @staticmethod
    def insert_query(table_name: str, columns: List, values: List):
        cn = ', '.join(columns)
        vn = []
        for v in values:
            if type(v) != str:
                vx = str(v)
            else:
                vx = "'" + v + "'"
            vn.append(vx)
        vn = ', '.join(vn)
        return f"INSERT INTO {table_name} ({cn}) VALUES ({vn});"

    def insert_sql(self, table, columns, values):
        inserts = [self.insert_query(table, columns, vn) for vn in values]
        self.execute_command(command=''.join(inserts))

    # def read(self, columns: List[str]):
    #
    #     return self.post_json('/read', dict(credentials=self.credentials, columns=json.dumps(columns)))

    # def query_graphl(self, query: str):
    #     request = requests.post(self.url() + "/graphql", json={'query': query})
    #     if request.status_code == 200:
    #         result = request.json()
    #     else:
    #         raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))
    #
    #     return result

    # def query_graphl(self, query: str):
    #     return self.post_json('/graphql', dict(query=query))
    #
    # def query_hasura(self, query_dict: List[Dict]):
    #     result = []
    #     for q in query_dict:
    #         r = self.post_json('/hasura_api', dict(query=q))
    #         result.append(r)
    #     return result
    #
    # def query_hasura_single(self, query_dict: Dict):
    #     return self.post_json('/hasura_api', dict(query=query_dict))


def database(url: str = "https://app.15rock.com/gateway/compute",
             credentials: Dict = None,
             credentials_file: str = None) -> DatabaseClient:
    credentials = credentials or helper.get_credentials(credentials, credentials_file)
    return DatabaseClient(url, credentials)


# def is_create_cmd(stmt):
#     return stmt.get_type() == 'CREATE'
#     pass


# def flatten(ll):
#     return [lu for l in ll for lu in l]

#
# def is_create_table_stmt(s):
#     # return s.get_type() == 'CREATE' and s.parent.get_type()
#     return 'create table' in s.value.lower()


# def get_tables_to_track(ddl):
#     parsed = sqlparse.parse(ddl)
#     create_stmts = list(filter(is_create_table_stmt, parsed))
#     all_tokens = flatten(map(lambda s: s.tokens, create_stmts))
#
#     table_tokens = list(filter(lambda t: t._get_repr_name() == 'Identifier', all_tokens))
#     #
#     return list(map(lambda tt: (tt.get_parent_name(), tt.get_name()), table_tokens))
#     pass


# def get_query(columns: List[str], meta, engine):
#     splits = [c.split('.') for c in columns]
#
#     full_columns = []
#     for s in splits:
#         if len(s) == 2:
#             schema_name = "public"
#             table_name = s[0]
#             column_name = s[1]
#         else:
#             schema_name = s[0]
#             table_name = s[1]
#             column_name = s[2]
#         full_columns.append(FullColumn(schema_name, table_name, column_name))
#
#     full_tables = []
#     for s in splits:
#         if len(s) == 2:
#             schema_name = "public"
#             table_name = s[0]
#         else:
#             schema_name = s[0]
#             table_name = s[1]
#         full_tables.append(FullTable(schema_name, table_name))
#
#     new_tables = inner_join_strs(set(full_tables), meta, engine)
#     fc_strs = ['.'.join([fc.schema_name, fc.table_name, fc.column_name]) for fc in full_columns]
#     new_columns = ', '.join(fc_strs)
#
#     query = f'''SELECT {new_columns} from {new_tables};'''
#
#     return query
#
#
# def get(user: str, columns: List[str]):
#     meta = MetaData()
#     q = get_query(columns, meta, db)
#     return read_sql(user, q)
#     pass


#
#
# def select_str(column_strs):
#     column_str = ', '.join(column_strs)
#     return f'''
# SELECT {column_str}
# '''
#
#
# def inner_join_str(pk_schema: str, pk_table: str, pk: str, fk_schema: str, fk_table: str, fk: str):
#     pk_table_full = f"{pk_schema}.{pk_table}"
#     fk_table_full = f"{fk_schema}.{fk_table}"
#     return f'''
# {pk_table_full} INNER JOIN {fk_table_full}
# ON {pk_table_full}.{pk} = {fk_table_full}.{fk}
# '''
#
#
# def to_alchemy_tables(tables: List[FullTable], meta, engine):
#     return [Table(t.table_name, meta, autoload=True, autoload_with=engine, schema=t.schema_name) for t in tables]
#
#
# def get_foreign_keys(alchemy_table):
#     return list(alchemy_table.foreign_keys)
#
#
# # pprint(inner_join_str(fk.column.table.schema, fk.column.table.name, fk.column.name, 'public', 'scoring_model',
# #                       fk.parent.name))
#
#
# def get_primary_full_table(fk):
#     return FullTable(fk.column.table.schema, fk.column.table.name)
#
#
# def exists(a_full_table, full_tables) -> bool:
#     for ft in full_tables:
#         if ft.schema_name == a_full_table.schema_name and ft.table_name == a_full_table.table_name:
#             return True
#     return False
#
#
# def inner_join_strs(full_tables, meta, engine):
#     final_joins = []
#     alchemy_tables = to_alchemy_tables(full_tables, meta, engine)
#     if len(full_tables) > 1:
#         for table in alchemy_tables:
#             fks = get_foreign_keys(table)
#             for fk in fks:
#                 pk_table = get_primary_full_table(fk)
#                 if exists(pk_table, full_tables):
#                     an_inner_join = inner_join_str(pk_table.schema_name, pk_table.table_name, fk.column.name,
#                                                    table.schema,
#                                                    table.name, fk.parent.name)
#                     final_joins.append(an_inner_join)
#         return final_joins[0]
#     else:
#         full_table = list(full_tables)[0]
#         return full_table.schema_name + '.' + full_table.table_name
#
#
# def query_graphl(query: str):
#     request = requests.post("http://localhost:8080/v1alpha1/graphql", json={'query': query})
#     if request.status_code == 200:
#         result = request.json()
#     else:
#         raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))
#
#     return result
#
#

def main(context, event):
    print('Hi')


if __name__ == '__main__':
    #     db_string = "postgres://postgres:@localhost:5432/postgres"
    #     # engine = create_engine(db_string)
    #     # meta = MetaData()
    #     assert get_query(columns=['public.customer.name']) == 'SELECT public.customer.name from public.customer;'
    #     assert get_query(columns=['public.customer.name',
    #                               'public.customer.age']) == 'SELECT public.customer.name, public.customer.age from public.customer;'
    #
    #     first_join_query = """SELECT public.customer.name, public.scoring_model.score from
    # public.customer INNER JOIN public.scoring_model
    # ON public.customer.id = public.scoring_model.customer_id
    # ;"""
    #     assert get_query(columns=["public.customer.name", "public.scoring_model.score"]) == first_join_query
    #     assert get_query(columns=["customer.name", "scoring_model.score"]) == first_join_query
    #     tables = [FullTable("public", "customer"),
    #               FullTable("public", "scoring_model")]
    #     final_join = inner_join_strs(tables)
    #
    #     exp_join = '''
    # public.customer INNER JOIN public.scoring_model
    # ON public.customer.id = public.scoring_model.customer_id
    # '''
    #     assert final_join == exp_join

    # def drop_relationship(schema, table, relationship):
    #     return {
    #         "type": "drop_relationship",
    #         "args": {
    #             "table": dict(schema=schema, name=table),
    #             "relationship": relationship
    #         }
    #     }

    # def untrack_table(schema, table):
    #     return {
    #         "type": "untrack_table",
    #         "args": {
    #             "table": {
    #                 "schema": schema,
    #                 "name": table
    #             },
    #             "cascade": True
    #         }
    #     }
    #

    # def track_table(schema, table):
    #     return {
    #         "type": "track_table",
    #         "args": {
    #             "schema": schema,
    #             "name": table
    #         }
    #     }

    # def create_array_relationship(relationship_name, schema, table, foreign_schema, foreign_table, foreign_column):
    #     # return {"type": "create_array_relationship", "args": {"name": "scoringModelsBycustomerId",
    #     #                                                       "table": {"name": "customer",
    #     #                                                                 "schema": "demo"},
    #     #                                                       "using": {
    #     #                                                           "foreign_key_constraint_on": {
    #     #                                                               "table": {
    #     #                                                                   "name": "scoring_model",
    #     #                                                                   "schema": "demo"},
    #     #                                                               "column": "customer_id"}}}}
    #
    #     return {"type": "create_array_relationship", "args": {"name": relationship_name,
    #                                                           "table": {"name": table,
    #                                                                     "schema": schema},
    #                                                           "using": {
    #                                                               "foreign_key_constraint_on": {
    #                                                                   "table": {
    #                                                                       "name": foreign_table,
    #                                                                       "schema": foreign_schema},
    #                                                                   "column": foreign_column}}}}
    #

    # create_array_relationship("scoringModelsBycustomerId", "demo", 'customer', 'demo', 'scoring_model', 'customer_id')

    # def create_object_relationship(relationship_name, schema, table, foreign_column):
    #     return {"type": "create_object_relationship", "args": {"name": relationship_name,
    #                                                            "table": {"name": table,
    #                                                                      "schema": schema}, "using": {
    #             "foreign_key_constraint_on": foreign_column}}}

    # create_object_relationship("customerBycustomerId", 'demo', 'scoring_model', 'customer_id')

    # def drop_table(schema, table):
    #     return {"type": "run_sql", "args": {"sql": f"DROP TABLE {schema}.{table}"}}

    # def get_object_relationship(constraint):
    #     fk = list(constraint['column_mapping'].keys())[0]
    #     label = constraint['ref_table'] + 'By' + fk
    #     return dict(label=label, schema=constraint['table_schema'], table_name=constraint['table_name'], foreign_key=fk)

    # def get_array_relationship(constraint):
    #     c = constraint
    #     table_name = c['table_name']
    #     fk = list(c['column_mapping'].keys())[0]
    #     label = table_name + 's' + 'By' + fk
    #     return dict(label=label, ref_schema=c['ref_table_table_schema'], ref_table=c['ref_table'], schema=c['table_schema'],
    #                 table_name=table_name, foreign_key=fk)
    #

    # def get_foreign_key_constraints(mappings):
    #     fkc_dicts = flatten([m['foreign_key_constraints'] for m in mappings if
    #                          'foreign_key_constraints' in m and m['foreign_key_constraints']])
    #     return fkc_dicts
    #
    #
    # def get_table_info_for_relationships(schema):
    #     return {"type": "select", "args": {"table": {"name": "hdb_table", "schema": "hdb_catalog"}, "columns": ["*.*",
    #                                                                                                             {
    #                                                                                                                 "name": "columns",
    #                                                                                                                 "columns": [
    #                                                                                                                     "*.*"],
    #                                                                                                                 "order_by": [
    #                                                                                                                     {
    #                                                                                                                         "column": "column_name",
    #                                                                                                                         "type": "asc",
    #                                                                                                                         "nulls": "last"}]}],
    #                                        "where": {"table_schema": schema},
    #                                        "order_by": [{"column": "table_name", "type": "asc", "nulls": "last"}]}}
    #
    # url = 'http://localhost:8082'
    url = 'https://146.148.70.166'

    main_path = '/Users/rabraham/Documents/dev/python/fifteenrock/main1.py'
    # print(os.path.basename(main_path))
    # print(os.path.splitext(os.path.basename(main_path))[0])

    # print(Path(main_path).stem)
    print(deploy({'user_name': 'rajiv'}, main_path, project='pd', function='f1', url=url))
    pass
