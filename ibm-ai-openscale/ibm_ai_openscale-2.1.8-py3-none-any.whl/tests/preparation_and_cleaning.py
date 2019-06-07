# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import io
import json
import os
import sys
import time
import uuid
from configparser import ConfigParser
from datetime import datetime, timedelta

import ibm_boto3

import jaydebeapi
import psycopg2
from ibm_botocore.client import Config
from psycopg2.sql import Identifier, SQL
from pytz import timezone


yesterday = datetime.now(timezone('UTC')) - timedelta(days=1)


if "ENV" in os.environ:
    environment = os.environ['ENV']
else:
    environment = "YP_QA"

print('Used environment:', environment)

if "icp" in str(environment).lower() or "db2" in str(environment).lower():
    import ibm_db

if "TEST_DIR" in os.environ:
    configDir = os.environ['TEST_DIR'] + "config.ini"
else:
    configDir = "./config.ini"

config = ConfigParser()
config.read(configDir)


def get_env():
    return environment


def get_schema_name():
    return config.get(environment, 'schema_name')


def get_schema_name2():
    return config.get(environment, 'schema_name2')


def get_aios_credentials():
    return json.loads(config.get(environment, 'aios_credentials'))


def get_aios_lite_credentials():
    if config.has_option(environment, 'aios_lite_credentials'):
        return json.loads(config.get(environment, 'aios_lite_credentials'))
    else:
        return None


def get_wml_payload_timeout():
    return json.loads(config.get('CONFIG', 'wml_payload_timeout'))


def get_3rd_payload_timeout():
    return json.loads(config.get('CONFIG', 'third_payload_timeout'))


def wait_for_payload_propagation(is_wml_engine=True):
    if is_wml_engine:
        timeout = get_wml_payload_timeout()
    else:
        timeout = get_3rd_payload_timeout()
    print("Waiting {} seconds for payload propagation...".format(timeout))
    time.sleep(timeout)


def get_database_credentials():
    if config.has_option(environment, 'database_credentials'):
        return json.loads(config.get(environment, 'database_credentials'))
    elif config.has_option(environment, 'postgres_credentials'):
        return get_postgres_credentials()
    elif config.has_option(environment, 'db2_datamart'):
        return get_db2_datamart_credentials()
    else:
        raise Exception("There is no database in config!")


def is_postgres_database():
    db_credentials = get_database_credentials()

    if "connection" in db_credentials.keys() and "postgres" in db_credentials['connection'].keys():
        return True

    if "db_type" in db_credentials.keys() and "postgresql" == db_credentials['db_type']:
        return True

    if 'postgres' in str(db_credentials):
        return True

    if 'dashdb' in str(db_credentials):
        return False

    if 'db2' in str(db_credentials):
        return False

    return False


def get_db2_datamart_credentials():
    return json.loads(config.get(environment, 'db2_datamart'))


def get_db2_schema_name():
    return json.loads(config.get(environment, 'db2_schema'))


def get_wml_credentials():
    return json.loads(config.get(environment, 'wml_credentials'))


def get_wml_lite_credentials():
    return json.loads(config.get(environment, 'wml_lite_credentials'))


def get_postgres_credentials():
    return json.loads(config.get(environment, 'postgres_credentials'))


def get_cos_credentials():
    return json.loads(config.get(environment, 'cos_credentials'))


def get_feedback_data_reference():
    return json.loads(config.get(environment, 'feedback_data_reference'))


def get_db2_credentials():
    return json.loads(config.get(environment, 'db2_reference'))


def get_spark_reference():
    return json.loads(config.get(environment, 'spark_reference'))


def get_cos_auth_endpoint():
    return config.get(environment, 'cos_auth_endpoint')


def get_cos_service_endpoint():
    return config.get(environment, 'cos_service_endpoint')


def get_client():
    wml_lib = __import__('watson_machine_learning_client', globals(), locals())
    return wml_lib.WatsonMachineLearningAPIClient(get_wml_credentials())


def get_wml_instance_plan(wml_credentials):
    wml_lib = __import__('watson_machine_learning_client', globals(), locals())
    wml_client = wml_lib.WatsonMachineLearningAPIClient(wml_credentials)
    wml_instance_details = wml_client.service_instance.get_details()
    return wml_instance_details['entity']['plan']


def get_cos_resource():
    cos_credentials = get_cos_credentials()
    api_key = cos_credentials['apikey']
    service_instance_id = cos_credentials['resource_instance_id']
    auth_endpoint = get_cos_auth_endpoint()
    service_endpoint = get_cos_service_endpoint()

    cos = ibm_boto3.resource(
        's3',
        ibm_api_key_id = api_key,
        ibm_service_instance_id = service_instance_id,
        ibm_auth_endpoint = auth_endpoint,
        config = Config(signature_version='oauth'),
        endpoint_url = service_endpoint
    )

    return cos


def prepare_cos(cos_resource, bucket_prefix='wml-test'):
    import datetime

    postfix = datetime.datetime.now().isoformat().replace(":", "-").split(".")[0].replace("T", "-")

    bucket_names = {
        'data': '{}-{}-data-{}'.format(bucket_prefix, environment.lower().replace('_', '-'), postfix),
        'results': '{}-{}-results-{}'.format(bucket_prefix, environment.lower().replace('_', '-'), postfix)
    }

    cos_resource.create_bucket(Bucket=bucket_names['data'])
    cos_resource.create_bucket(Bucket=bucket_names['results'])

    return bucket_names


def get_cos_training_data_reference(bucket_names):
    cos_credentials = get_cos_credentials()
    service_endpoint = get_cos_service_endpoint()

    return {
        "connection": {
            "endpoint_url": service_endpoint,
            "access_key_id": cos_credentials['cos_hmac_keys']['access_key_id'],
            "secret_access_key": cos_credentials['cos_hmac_keys']['secret_access_key']
        },
        "source": {
            "bucket": bucket_names['data'],
        },
        "type": "s3"
    }


def get_cos_training_results_reference(bucket_names):
    cos_credentials = get_cos_credentials()
    service_endpoint = get_cos_service_endpoint()

    return {
        "connection": {
            "endpoint_url": service_endpoint,
            "access_key_id": cos_credentials['cos_hmac_keys']['access_key_id'],
            "secret_access_key": cos_credentials['cos_hmac_keys']['secret_access_key']
        },
        "target": {
            "bucket": bucket_names['results'],
        },
        "type": "s3"
    }


def clean_cos_bucket(cos_resource, bucket_name):
    bucket_obj = cos_resource.Bucket(bucket_name)
    for upload in bucket_obj.multipart_uploads.all():
        upload.abort()
    for o in bucket_obj.objects.all():
        o.delete()
    bucket_obj.delete()


def clean_cos(cos_resource, bucket_names):
    clean_cos_bucket(cos_resource, bucket_names['data'])
    clean_cos_bucket(cos_resource, bucket_names['results'])


def clean_env(cos_resource=None, threshold_date=yesterday, raise_when_not_empty=False, database="postgres"):
    rm_els_no = 0

    from ibm_ai_openscale import APIClient
    ai_client = APIClient(get_aios_credentials())
    for uid in ai_client.data_mart.subscriptions.get_uids():
        subscription = ai_client.data_mart.subscriptions.get(uid)
        if subscription.get_details()['metadata']['created_at'] < threshold_date.isoformat():
            print('Deleting \'{}\' subscription.'.format(uid))
            try:
                ai_client.data_mart.subscriptions.delete(uid)
            except Exception as e:
                print('Deleting of subscription failed:', e)

    client = get_client()

    rm_els_no += clean_experiments(client, threshold_date)
    rm_els_no += clean_training_runs(client, threshold_date)
    rm_els_no += clean_definitions(client, threshold_date)
    rm_els_no += clean_models(client, threshold_date)
    rm_els_no += clean_deployments(client, threshold_date)
    try:
        rm_els_no += clean_ai_functions(client, threshold_date)
        rm_els_no += clean_runtimes(client, threshold_date)
        rm_els_no += clean_custom_libraries(client, threshold_date)
    except:
        pass

    if cos_resource is not None:
        for bucket in cos_resource.buckets.all():
            if 'wml-test-' in bucket.name and bucket.creation_date < threshold_date:
                rm_els_no +=1
                print('Deleting \'{}\' bucket.'.format(bucket.name))
                try:
                    for upload in bucket.multipart_uploads.all():
                        upload.abort()
                    for o in bucket.objects.all():
                        o.delete()
                    bucket.delete()
                except Exception as e:
                    print("Exception during bucket deletion occured: " + str(e))

    if raise_when_not_empty and rm_els_no > 0:
        raise Exception('Non zero number of elements to clean: {}'.format(rm_els_no))

    try:
        ai_client = APIClient(get_aios_credentials())
        try:
            for uid in ai_client.data_mart.bindings.get_uids():
                ai_client.data_mart.bindings.delete(uid)
        except:
            pass

        try:
            ai_client.data_mart.delete()
        except:
            pass
    except:
        pass

    if database == "postgres":
        clean_postgress_instance()
        set_up_postgress_instance()
    elif database == "db2":
        clean_db2_schema(get_db2_datamart_credentials(), get_db2_schema_name())
    elif database == "all":
        clean_postgress_instance()
        set_up_postgress_instance()
        clean_db2_schema(get_db2_datamart_credentials(), get_db2_schema_name())
    else:
        raise Exception("Database {} not supported!".format(database))


def prepare_env(ai_client, internal=False):

    for uid in ai_client.data_mart.subscriptions.get_uids():
        print('Deleting \'{}\' subscription.'.format(uid))
        try:
            ai_client.data_mart.subscriptions.delete(uid)
        except Exception as e:
            print('Deleting of subscription failed:', e)

    for uid in ai_client.data_mart.bindings.get_uids():
        try:
            ai_client.data_mart.bindings.delete(uid)
        except:
            pass
    try:
        ai_client.data_mart.delete()
    except:
        pass

    if internal:
        return

    db_credentials = get_database_credentials()
    schema_name = get_schema_name()

    if "postgres" in str(db_credentials):
        delete_schema(db_credentials, schema_name)
        create_schema(db_credentials, schema_name)

    elif "db2" in str(db_credentials):
        clean_db2_database(db2_credentials=db_credentials, db2_schema=schema_name)

    # if "ICP" in get_env():
    #     if "bluemix.net" in str(db_credentials):
    #         clean_db2_schema(db_credentials, schema_name)
    #     else:
    #         clean_db2_icp_schema(db_credentials, schema_name)
    # else:
    #     if 'postgres' in str(db_credentials):
    #         delete_schema(db_credentials, schema_name)
    #         create_schema(db_credentials, schema_name)
    #     elif 'db2' in db_credentials['uri']:
    #         cleaned_db2 = False
    #         try:
    #             clean_db2_schema(db_credentials, schema_name)
    #             cleaned_db2 = True
    #         except Exception:
    #             pass
    #
    #         if not cleaned_db2:
    #             try:
    #                 time.sleep(30)
    #                 clean_db2_schema(db_credentials, schema_name)
    #             except Exception:
    #                 pass
    #     else:
    #         raise Exception("Database {} not supported!".format(db_credentials))


def clean_postgress_instance():
    delete_schema(get_postgres_credentials(), get_schema_name())
    delete_schema(get_postgres_credentials(), get_schema_name2())


def set_up_postgress_instance():
    create_schema(get_postgres_credentials(), get_schema_name())
    create_schema(get_postgres_credentials(), get_schema_name2())


def clean_wml_assets(details, delete, asset_name, threshold_date=yesterday):

    number_of_assets = 0

    for asset_details in details['resources']:
        if asset_details['metadata']['created_at'] < threshold_date.isoformat():
            number_of_assets += 0
            print('Deleting \'{}\' {}.'.format(asset_details['metadata']['guid'], asset_name))
            try:
                delete(asset_details['metadata']['guid'])
            except Exception as e:
                print('Deletion of {} failed:'.format(asset_name), e)

    return number_of_assets


def clean_repository_assets(client, details, asset_name, threshold_date=yesterday):
    return clean_wml_assets(details, client.repository.delete, asset_name, threshold_date)


def clean_models(client, threshold_date=yesterday):
    return clean_repository_assets(client, client.repository.get_model_details(), 'model', threshold_date)


def clean_definitions(client, threshold_date=yesterday):
    return clean_repository_assets(client, client.repository.get_definition_details(), 'definition', threshold_date)


def clean_deployments(client, threshold_date=yesterday):
    return clean_wml_assets(client.deployments.get_details(), client.deployments.delete, 'deployment', threshold_date)


def clean_experiments(client, threshold_date=yesterday):
    return clean_repository_assets(client, client.repository.get_experiment_details(), 'experiment', threshold_date)


def clean_training_runs(client, threshold_date=yesterday):
    return clean_wml_assets(client.training.get_details(), client.training.delete, 'training run', threshold_date)


def clean_runtimes(client, threshold_date=yesterday):
    return clean_repository_assets(client, client.runtimes.get_details(), 'runtimes', threshold_date)


def clean_custom_libraries(client, threshold_date=yesterday):
    return clean_wml_assets(client.runtimes.get_library_details(), client.runtimes.delete_library, 'custom library', threshold_date)


def clean_ai_functions(client, threshold_date=yesterday):
    return clean_repository_assets(client, client.repository.get_function_details(), 'python function', threshold_date)


def run_monitor(client, experiment_run_uid, queue):
    stdout_ = sys.stdout
    captured_output = io.StringIO()  # Create StringIO object
    sys.stdout = captured_output  # and redirect stdout.
    client.experiments.monitor_logs(experiment_run_uid)
    sys.stdout = stdout_  # Reset redirect.

    print(captured_output.getvalue())

    queue.put(captured_output.getvalue())


def run_monitor_metrics(client, experiment_run_uid, queue):
    stdout_ = sys.stdout
    captured_output = io.StringIO()  # Create StringIO object
    sys.stdout = captured_output  # and redirect stdout.
    client.experiments.monitor_metrics(experiment_run_uid)
    sys.stdout = stdout_  # Reset redirect.

    print(captured_output.getvalue())

    queue.put(captured_output.getvalue())


def run_monitor_training(client, training_run_uid, queue):
    stdout_ = sys.stdout
    captured_output = io.StringIO()  # Create StringIO object
    sys.stdout = captured_output  # and redirect stdout.
    client.training.monitor_logs(training_run_uid)
    sys.stdout = stdout_  # Reset redirect.

    print(captured_output.getvalue())

    queue.put(captured_output.getvalue())


def prepare_connection_postgres(postgres_credentials):

    if 'uri' in postgres_credentials.keys():
        uri = postgres_credentials['uri']

        import re
        res = re.search('^[0-9a-zA-Z]+://([0-9a-zA-Z]+):([0-9a-zA-Z]+)@([^:]+):([0-9]+)/([0-9a-zA-Z]+)$', uri)

        if res is None:
            raise Exception('Unexpected format of db uri: {}'.format(uri))

        username = res.group(1)
        password = res.group(2)
        host = res.group(3)
        port = res.group(4)
        database = res.group(5)

        return psycopg2.connect(
            database=database,
            user=username,
            password=password,
            host=host,
            port=port
        )
    elif 'connection' in postgres_credentials.keys():
        pstg_connection = postgres_credentials['connection']['postgres']
        conn_str = "host='{}' port='{}' dbname='{}' user='{}' password='{}' sslmode='require'".format(pstg_connection['hosts'][0]['hostname'], pstg_connection['hosts'][0]['port'],
                                                                                                      pstg_connection['database'], pstg_connection['authentication']['username'],
                                                                                                      pstg_connection['authentication']['password'])
        return psycopg2.connect(conn_str)


def prepare_connection_db2(db2_credentials):
    db2jcc_path = os.path.join(os.getcwd(), 'tools', 'db2jcc4.jar')
    return jaydebeapi.connect(
        'com.ibm.db2.jcc.DB2Driver',
        db2_credentials['jdbcurl'],
        [db2_credentials['username'], db2_credentials['password']],
        db2jcc_path
    )


def create_schema(postgres_credentials, schema_name):
    try:
        execute_sql_query(SQL("CREATE SCHEMA {}").format(Identifier(schema_name)), postgres_credentials)
    except psycopg2.Error as ex:
        print("Unable to create schema {}. Reason:\n{}".format(schema_name, ex.pgerror))


def delete_schema(postgres_credentials, schema_name):
    try:
        execute_sql_query(SQL("DROP SCHEMA {} CASCADE").format(Identifier(schema_name)), postgres_credentials)
        print("Schema {} dropped.".format(schema_name))
    except psycopg2.Error:
        print("Schema {} does not exist.".format(schema_name))


def delete_db2_schema(db2_credentials, schema_name):
    execute_sql_query("DROP SCHEMA {} CASCADE".format(schema_name), db2_credentials=db2_credentials)


def clean_db2_icp_schema(db2_credentials, schema_name):
    result = execute_sql_query(""" select 'DROP TABLE "'||rtrim(tabschema)||'"."'||rtrim(tabname)||'"' from syscat.tables where OWNER = 'DB2INST1' and TABSCHEMA = '{}' and type = 'T' """.format(schema_name), db2_credentials=db2_credentials)
    for query in result:
        execute_sql_query(query[0], db2_credentials=db2_credentials)


def clean_db2_schema(db2_credentials, schema_name):
    for query in list(map(lambda table: """ DROP TABLE "{}"; """.format(table), list_db2_tables(db2_credentials=db2_credentials, schema_name=schema_name))):
        execute_sql_query(query, db2_credentials=db2_credentials)


def list_db2_tables(db2_credentials, schema_name):
    query_result = execute_sql_query(""" SELECT tabname FROM syscat.tables WHERE owner='{}' AND type='T' """.format(schema_name), db2_credentials=db2_credentials)
    db2_tables = []
    for record in query_result:
        db2_tables.append(record[0])

    return db2_tables


def print_schema_tables_info(postgres_credentials, schema_name):
    rows = execute_sql_query("SELECT * FROM information_schema.tables WHERE table_schema = '{}'".format(schema_name), postgres_credentials)
    query_rows = []
    for row in rows:
        query_rows.append(row)

    return query_rows


def wait_until_deleted(ai_client, binding_uid=None, subscription_uid=None, data_mart=None):
    uids_sum = sum([1 if b else 0 for b in [binding_uid, subscription_uid, data_mart]])

    if uids_sum > 1:
        raise Exception('More than one uid passed.')
    elif uids_sum == 0:
        raise Exception('No uids passed.')

    def can_be_found():
        if binding_uid is not None:
            try:
                print(ai_client.data_mart.bindings.get_details(binding_uid))
                return True
            except:
                return False
        elif subscription_uid is not None:
            try:
                print(ai_client.data_mart.subscriptions.get_details(subscription_uid))
                return True
            except:
                return False
        elif data_mart is not None:
            try:
                print(ai_client.data_mart.get_details())
                return True
            except Exception as e:
                print(e)
                return False

    import time

    print('Waiting for {} to delete...'.format(
        'binding with uid=\'{}\''.format(binding_uid) if binding_uid is not None
        else 'subscription with uid=\'{}\''.format(subscription_uid) if subscription_uid is not None
        else 'data_mart'
    ), end='')

    iterator = 0

    while can_be_found() and iterator < 20:
        time.sleep(3)
        print('.', end='')
        iterator += 1

    print(' DELETED')


def execute_sql_query(query, postgres_credentials=None, db2_credentials=None):
    if postgres_credentials is not None:
        conn = prepare_connection_postgres(postgres_credentials=postgres_credentials)
    elif db2_credentials is not None:
        conn = prepare_connection_db2(db2_credentials=db2_credentials)
    else:
        raise Exception("Credentials are not supported.")

    cursor = conn.cursor()
    cursor.execute(query)

    try:
        query_result = cursor.fetchall()
    except psycopg2.ProgrammingError as ex:
        query_result = ""
    except jaydebeapi.Error as ex:
        query_result = ""

    conn.commit()
    cursor.close()
    conn.close()

    return query_result


def upload_german_risk_training_data_to_postgres(postgres_credentials):
    try:
        execute_sql_query(""" SELECT * FROM {}.CreditRiskTable LIMIT 1 """.format("trainingdataschema"), postgres_credentials=postgres_credentials)
        return
    except psycopg2.ProgrammingError:
        print("Table does not exist. Creating new schema and table.")

    try:
        create_schema(postgres_credentials, "trainingdataschema")
    except psycopg2.ProgrammingError:
        print("Schema already exist.")

    try:
        execute_sql_query("""
                CREATE TABLE {}.{}(
                    CheckingStatus text,
                    LoanDuration integer,
                    CreditHistory text,
                    LoanPurpose text,
                    LoanAmount integer,
                    ExistingSavings text,
                    EmploymentDuration text,
                    InstallmentPercent integer,
                    Sex text,
                    OthersOnLoan text,
                    CurrentResidenceDuration integer,
                    OwnsProperty text,
                    Age integer,
                    InstallmentPlans text,
                    Housing text,
                    ExistingCreditsCount integer,
                    Job text,
                    Dependents integer,
                    Telephone text,
                    ForeignWorker text,
                    Risk text
                )
                """.format("trainingdataschema", "CreditRiskTable"), postgres_credentials=postgres_credentials)

    except psycopg2.ProgrammingError as ex:
        print("Unable to create new table!")
        print(ex)

    try:
        conn = prepare_connection_postgres(postgres_credentials)
        conn.autocommit = True
        cursor = conn.cursor()
        with open(os.path.join(os.curdir, 'datasets', 'German_credit_risk', 'credit_risk_training.csv'), 'r') as f:
            next(f)
            cursor.copy_from(file=f, table='{}.CreditRiskTable'.format("trainingdataschema"), sep=',')
        cursor.close()
        conn.close()
    except psycopg2.ProgrammingError as ex:
        print("Unable to upload content from CSV to postgres table")
        print(ex)

    try:
        result = execute_sql_query(""" SELECT * FROM {}.CreditRiskTable LIMIT 1 """.format("trainingdataschema"), postgres_credentials=postgres_credentials)
        print("Table content:\n{}".format(result))
        return
    except psycopg2.ProgrammingError as ex:
        print("Error during table creation!")
        raise ex


def upload_go_sales_training_data_to_postgres(postgres_credentials):
    try:
        execute_sql_query(""" SELECT * FROM {}.GoSalesTable LIMIT 1 """.format("trainingdataschema"), postgres_credentials=postgres_credentials)
        return
    except psycopg2.ProgrammingError:
        print("Table does not exist. Creating new schema and table.")

    try:
        create_schema(postgres_credentials, "trainingdataschema")
    except psycopg2.ProgrammingError:
        print("Schema already exist.")

    try:
        execute_sql_query("""
                CREATE TABLE {}.{}(
                    PRODUCT_LINE text,
                    GENDER text,
                    AGE integer,
                    MARITAL_STATUS text,
                    PROFESSION text
                )
                """.format("trainingdataschema", "GoSalesTable"), postgres_credentials=postgres_credentials)

    except psycopg2.ProgrammingError as ex:
        print("Unable to create new table!")
        print(ex)

    try:
        conn = prepare_connection_postgres(postgres_credentials)
        conn.autocommit = True
        cursor = conn.cursor()
        with open(os.path.join(os.curdir, 'datasets', 'GoSales', 'GoSales_Tx_NaiveBayes.csv'), 'r') as f:
            next(f)
            cursor.copy_from(file=f, table='{}.GoSalesTable'.format("trainingdataschema"), sep=',')
        cursor.close()
        conn.close()
    except psycopg2.ProgrammingError as ex:
        print("Unable to upload content from CSV to postgres table")
        print(ex)

    try:
        result = execute_sql_query(""" SELECT * FROM {}.GoSalesTable LIMIT 1 """.format("trainingdataschema"), postgres_credentials=postgres_credentials)
        print("Table content:\n{}".format(result))
        return
    except psycopg2.ProgrammingError as ex:
        print("Error during table creation!")
        raise ex


def export_datamart_config_to_json(ai_client):
    import requests
    response = requests.get(url="{}/{}".format(ai_client._href_definitions.get_data_mart_href(), 'file'), headers=ai_client._get_headers())

    return response.json()


def clean_wml_instance(model_id, deployment_id, binding_id=None):
    print("Cleaning WML instance ...")
    if binding_id is not None:
        from ibm_ai_openscale import APIClient
        ai_client = APIClient(get_aios_credentials())
        wml_client = ai_client.data_mart.bindings.get_native_engine_client(binding_id)
    else:
        wml_client = get_client()

    print("Deleting deployment: {}".format(deployment_id))
    wml_client.deployments.delete(deployment_id)

    print("Deleting model: {}".format(model_id))
    wml_client.repository.delete(model_id)

    # if "ICP" in get_env():
    #     clean_up_wml_instance()


def clean_up_wml_instance():
    wml_client = get_client()

    print("Cleaning wml instance.")
    print("Removing all deployments...")

    for deployment in wml_client.deployments.get_details()['resources']:
        wml_client.deployments.delete(deployment['metadata']['guid'])

    details = wml_client.repository.get_details()

    print("Removing all models...")
    for model in details['models']['resources']:
        wml_client.repository.delete(model['metadata']['guid'])

    print("Removing all runtimes...")
    for runtime in details['runtimes']['resources']:
        wml_client.repository.delete(runtime['metadata']['guid'])

    # print("Removing definitions...")
    # for definition in details['definitions']['resources']:
    #     wml_client.repository.delete(definition['metadata']['guid'])

    print("Cleaning done.")


def clean_db2_database(db2_credentials, db2_schema):
    db2_dsn = db2_credentials["dsn"]

    if "icp" in str(get_env()).lower():
        tables_drop_query = execute_db2_sql_query(query= """ select 'DROP TABLE "'||rtrim(tabschema)||'"."'||rtrim(tabname)||'"' from syscat.tables where OWNER = 'DB2INST1' and TABSCHEMA = '{}' and type = 'T' """.format(db2_schema), db2_dsn=db2_dsn)
        views_drop_query = execute_db2_sql_query(query=""" select 'DROP VIEW "'||rtrim(tabschema)||'"."'||rtrim(tabname)||'"' from syscat.tables where OWNER = 'DB2INST1' and TABSCHEMA = '{}' and type = 'V' """.format(db2_schema), db2_dsn=db2_dsn)

        for table_query in tables_drop_query:
            execute_db2_immediately_query(query=table_query, db2_dsn=db2_dsn)

        for view_query in views_drop_query:
            execute_db2_immediately_query(query=view_query, db2_dsn=db2_dsn)

    else:
        tables = execute_db2_sql_query(query="SELECT tabname FROM syscat.tables WHERE owner='{}' AND type='T' ".format(db2_schema), db2_dsn=db2_dsn)
        views = execute_db2_sql_query(query="SELECT tabname FROM syscat.tables WHERE owner='{}' AND type='V' ".format(db2_schema), db2_dsn=db2_dsn)
        for table in tables:
            execute_db2_immediately_query(query="""DROP TABLE "{}";""".format(table), db2_dsn=db2_dsn)

        for view in views:
            execute_db2_immediately_query(query="""DROP VIEW "{}";""".format(view), db2_dsn=db2_dsn)


def upload_credit_risk_training_data_to_db2(db2_credentials):
    db2_dsn = db2_credentials["dsn"]
    db2_uri = db2_credentials["uri"]
    if "icp" in str(get_env()).lower():
        schemas_list = execute_db2_sql_query(query= """ select schemaname from syscat.schemata """, db2_dsn=db2_dsn)

        if "TRAININGDATA" in schemas_list:
            print("Training data schema exists")
            return
            # execute_db2_immediately_query(query=""" drop schema TRAININGDATA restrict""", db2_dsn=db2_dsn)


        print("Creating schema")
        execute_db2_immediately_query(query=""" create schema TRAININGDATA """, db2_dsn=db2_dsn)

        import sqlalchemy
        import pandas as pd
        import ibm_db_sa

        engine = sqlalchemy.create_engine('ibm_db_sa:{}'.format(db2_uri[4:]))

        df = pd.read_csv("datasets/German_credit_risk/credit_risk_training_500.csv")
        df.to_sql(name="CREDIT_RISK_TRAINING", con=engine, schema="TRAININGDATA", index=False, if_exists="replace")

        print("Training data uploaded successfully.")


def execute_db2_sql_query(query, db2_dsn):
    results_array = []

    connection = ibm_db.connect(db2_dsn, "", "")
    statement = ibm_db.prepare(connection, query)

    try:
        ibm_db.execute(statement)

        result_dict = ibm_db.fetch_tuple(statement)
        while result_dict is not False:
            results_array.append(result_dict[0])
            result_dict = ibm_db.fetch_tuple(statement)
    except Exception as ex:
        print("SQL execution failed:")
        print(ex)
    finally:
        ibm_db.close(connection)

    return results_array


def execute_db2_immediately_query(query, db2_dsn):
    connection = ibm_db.connect(db2_dsn, "", "")
    try:
        ibm_db.exec_immediate(connection, query)
    except Exception as ex:
        print("SQL immediately execution failed:")
        print(ex)
    finally:
        ibm_db.close(connection)


def get_details_from_restapi(ai_client, binding_uid):
    import requests
    response = requests.get(ai_client._href_definitions.get_ml_gateway_discovery_href(binding_uid=binding_uid), headers=ai_client._get_headers())
    print("Request url: {}".format(ai_client._href_definitions.get_ml_gateway_discovery_href(binding_uid=binding_uid)))
    print("Request header: {}".format(ai_client._get_headers()))
    print("Response code: {}".format(response.status_code))
    print("Response text: {}".format(response.json()))