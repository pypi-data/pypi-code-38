#DB & Audit
import os
import requests
from requests.auth import HTTPDigestAuth
import pprint
from sumoclient.httputils import ClientMixin
from sumoclient.factory import OutputHandlerFactory
from sumoclient.utils import get_current_timestamp, convert_epoch_to_utc_date, convert_utc_date_to_epoch
from datetime import datetime
import gzip
import json
from io import BytesIO
from common.config import Config

# project -> hosts -> processes -> databases

yamlconfig = Config().get_config("mongodbatlas.yaml", os.path.dirname(__file__), '')


def getdata(url, **kwargs):
    status, data = ClientMixin.make_request(url, method="get", TIMEOUT=60, **kwargs)
    return data if status else []


def getpaginateddata(url, **kwargs):
    page_num = 0
    all_data = []
    try:
        sess = ClientMixin.get_new_session()
        while True:
            page_num += 1
            status, data = ClientMixin.make_request(url, method="get", session=sess, TIMEOUT=60, **kwargs)
            if status and "results" in data and len(data['results']) > 0:
                all_data.append(data)
                kwargs['params']['pageNum'] = page_num + 1
            else:
                break
    finally:
        sess.close()
    return all_data


def get_all_databases(config, process_ids):
    database_names = []
    for process_id in process_ids:
        url = f'''{config['baseurl']}/groups/{config['project_id']}/processes/{process_id}/databases'''
        kwargs = {'auth': HTTPDigestAuth(config['username'], config['api_key']), "params": {"itemsPerPage": 500}}
        all_data = getpaginateddata(url, **kwargs)
        database_names.extend([obj['databaseName'] for data in all_data for obj in data['results']])
    return list(set(database_names))


def get_all_processes_from_project(config):
    url = f'''{config['baseurl']}/groups/{config['project_id']}/processes'''
    kwargs = {'auth': HTTPDigestAuth(config['username'], config['api_key']), "params": {"itemsPerPage": 500}}
    all_data = getpaginateddata(url, **kwargs)
    process_ids = [obj['id'] for data in all_data for obj in data['results']]
    hostnames = [obj['hostname'] for data in all_data for obj in data['results']]
    # 'port': 27017, 'replicaSetName': 'M10AWSTestCluster-config-0', 'typeName': 'SHARD_CONFIG_PRIMARY'

    hostnames = list(set(hostnames))
    return process_ids, hostnames


def get_all_disks_from_host(config, process_ids):
    disks = []
    for process_id in process_ids:
        url = f'''{config['baseurl']}/groups/{config['project_id']}/processes/{process_id}/disks'''
        kwargs = {'auth': HTTPDigestAuth(config['username'], config['api_key']), "params": {"itemsPerPage": 500}}
        all_data = getpaginateddata(url, **kwargs)
        disks.extend([obj['partitionName'] for data in all_data for obj in data['results']])
    return list(set(disks))


# Metrics
def get_disk_metrics(config, process_ids, disks, start_time_date, end_time_date):
    # Get measurements of specified disk for the specified host.
    date_format = '%Y-%m-%dT%H:%M:%SZ'
    metrics = []
    for process_id in process_ids:
        for disk_name in disks:
            url = f'''{config['baseurl']}/groups/{config['project_id']}/processes/{process_id}/disks/{disk_name}/measurements'''
            kwargs = {'auth': HTTPDigestAuth(config['username'], config['api_key']), "params": {
                "itemsPerPage": 500, "granularity": "PT1M", "start": start_time_date, "end": end_time_date
            }}
            data = getdata(url, **kwargs)
            for measurement in data['measurements']:
                for datapoints in measurement['dataPoints']:
                    if datapoints['value'] is None:
                        continue
                    metrics.append(f'''projectId={data['groupId']} partitionName={data['partitionName']} hostId={data['hostId']} processId={data['processId']} metric={measurement['name']}  units={measurement['units']} {datapoints['value']} {convert_utc_date_to_epoch(datapoints['timestamp'], date_format=date_format)}''')

    yamlconfig['SumoLogic']["SUMO_ENDPOINT"] = yamlconfig['SumoLogic']["METRICS_SUMO_ENDPOINT"]
    output_handler = OutputHandlerFactory.get_handler(yamlconfig['Collection']['OUTPUT_HANDLER'], path="%s.json" % "db_metrics", config=yamlconfig)
    send_success = output_handler.send(metrics, extra_headers={'Content-Type': 'application/vnd.sumologic.carbon2'}, jsondump=False)
    print(send_success)
    return metrics


def get_database_metrics(config, process_ids, database_names, start_time_date, end_time_date):
    # Get measurements of the specified database for the specified host.
    date_format = '%Y-%m-%dT%H:%M:%SZ'
    metrics = []
    for process_id in process_ids:
        for database_name in database_names:
            url = f'''{config['baseurl']}/groups/{config['project_id']}/processes/{process_id}/databases/{database_name}/measurements'''
            kwargs = {'auth': HTTPDigestAuth(config['username'], config['api_key']), "params": {
                "itemsPerPage": 500, "granularity": "PT1M", "start": start_time_date, "end": end_time_date
            }}
            data = getdata(url, **kwargs)
            for measurement in data['measurements']:
                for datapoints in measurement['dataPoints']:
                    if datapoints['value'] is None:
                        continue
                    metrics.append(f'''projectId={data['groupId']} databaseName={data['databaseName']} hostId={data['hostId']} processId={data['processId']} metric={measurement['name']}  units={measurement['units']} {datapoints['value']} {convert_utc_date_to_epoch(datapoints['timestamp'], date_format=date_format)}''')

    yamlconfig['SumoLogic']["SUMO_ENDPOINT"] = yamlconfig['SumoLogic']["METRICS_SUMO_ENDPOINT"]
    output_handler = OutputHandlerFactory.get_handler(yamlconfig['Collection']['OUTPUT_HANDLER'], path="%s.json" % "db_metrics", config=yamlconfig)
    send_success = output_handler.send(metrics, extra_headers={'Content-Type': 'application/vnd.sumologic.carbon2'},jsondump=False)
    print(send_success)
    return metrics


def get_process_metrics(config, process_ids, start_time_date, end_time_date):
    # Get measurements for the specified host.
    date_format = '%Y-%m-%dT%H:%M:%SZ'
    metrics = []
    for process_id in process_ids:
        url = f'''{config['baseurl']}/groups/{config['project_id']}/processes/{process_id}/measurements'''
        kwargs = {'auth': HTTPDigestAuth(config['username'], config['api_key']), "params": {
            "itemsPerPage": 500, "granularity": "PT1M", "start": start_time_date, "end": end_time_date
        }}
        data = getdata(url, **kwargs)
        for measurement in data['measurements']:
            for datapoints in measurement['dataPoints']:
                    if datapoints['value'] is None:
                        continue
                    metrics.append(f'''projectId={data['groupId']} hostId={data['hostId']} processId={data['processId']} metric={measurement['name']}  units={measurement['units']} {datapoints['value']} {convert_utc_date_to_epoch(datapoints['timestamp'], date_format=date_format, milliseconds=True)}''')

    yamlconfig['SumoLogic']["SUMO_ENDPOINT"] = yamlconfig['SumoLogic']["METRICS_SUMO_ENDPOINT"]
    output_handler = OutputHandlerFactory.get_handler(yamlconfig['Collection']['OUTPUT_HANDLER'], path="%s.json" % "db_metrics", config=yamlconfig)
    send_success = output_handler.send(metrics, extra_headers={'Content-Type': 'application/vnd.sumologic.carbon2'}, jsondump=False)
    print(send_success)
    return metrics


# Logs
def get_logs_from_host(config, hostnames, start_time_epoch, end_time_epoch):
    # Get the log file (db logs and audit logs) for a host in the cluster.

    filenames = [ "mongodb-audit-log.gz", "mongos-audit-log.gz","mongodb.gz", "mongos.gz",] # "mongosqld.gz"
    yamlconfig['SumoLogic']["SUMO_ENDPOINT"] = yamlconfig['SumoLogic']["LOGS_SUMO_ENDPOINT"]
    output_handler = OutputHandlerFactory.get_handler(yamlconfig['Collection']['OUTPUT_HANDLER'], path="%s.json" % "db_logs", config=yamlconfig)
    for filename in filenames:
        all_logs = []

        for hostname in hostnames[:1]:
            url = f'''{config['baseurl']}/groups/{config['project_id']}/clusters/{hostname}/logs/{filename}'''
            kwargs = {
                'auth': HTTPDigestAuth(config['username'], config['api_key']),
                 "params": {"startDate": start_time_epoch, "endDate": end_time_epoch},
                 "headers": {"Accept": "application/gzip"},
                 "is_file": True
            }
            content = getdata(url, **kwargs)
            if len(content) > 0:
                print(hostname, filename, len(content))
                # data = gzip.decompress(content) assuming file content is small so inmemory possible
                # https://stackoverflow.com/questions/11914472/stringio-in-python3
                # https://stackoverflow.com/questions/8858414/using-python-how-do-you-untar-purely-in-memory
                results = gzip.GzipFile(fileobj=BytesIO(content))

                for line in results.readlines():
                    if "audit" in filename:
                        msg = json.loads(line.decode('utf-8'))
                        msg['project_id'] = config['project_id']
                        msg['hostname'] = hostname
                        all_logs.append(msg)
                    else:
                        all_logs.append({
                            'msg': line.decode('utf-8').strip(),
                            'project_id': config['project_id'],
                            'hostname': hostname
                        })

        send_success = output_handler.send(all_logs, extra_headers={'X-Sumo-Name': filename})
        print(send_success)


# Audit settings
# def get_project_audit_settings(config):
#     # Get Auditing Configuration for a Project
#     url = f'''{config['baseurl']}/groups/{config['project_id']}/auditLog'''
#     kwargs = {'auth': HTTPDigestAuth(config['username'], config['api_key'])}
#     data = getdata(url, **kwargs)
#     print(data)


# Performance Advisor
def get_slow_query_namespaces_from_process(config, process_ids, start_time_epoch, end_time_epoch):
    # Retrieves the namespaces for collections experiencing slow queries for a specified host.

    since = start_time_epoch*1000
    duration = (end_time_epoch - start_time_epoch)*1000 # in ms
    sq_namespaces = []
    for process_id in process_ids:
        url = f'''{config['baseurl']}/groups/{config['project_id']}/processes/{process_id}/performanceAdvisor/namespaces'''
        kwargs = {'auth': HTTPDigestAuth(config['username'], config['api_key']), "params": {
             "since": since, "duration": duration
        }}
        data = getdata(url, **kwargs)
        for ns in data['namespaces']:
            ns['project_id'] = config['project_id']
            ns['process_id'] = process_id
            ns['timestamp'] = start_time_epoch
            sq_namespaces.append(ns)

    yamlconfig['SumoLogic']["SUMO_ENDPOINT"] = yamlconfig['SumoLogic']["LOGS_SUMO_ENDPOINT"]
    output_handler = OutputHandlerFactory.get_handler(yamlconfig['Collection']['OUTPUT_HANDLER'], path="%s.json" % "slow_query_namespaces", config=yamlconfig)
    send_success = output_handler.send(sq_namespaces)
    print(send_success)

    return sq_namespaces


def get_slow_queries_from_process(config, process_ids, start_time_epoch, end_time_epoch):
    # Get log lines for slow queries as determined by the Performance Advisor.
    since = start_time_epoch*1000
    duration = (end_time_epoch - start_time_epoch)*1000 # in ms
    sq_logs = []
    for process_id in process_ids:
        url = f'''{config['baseurl']}/groups/{config['project_id']}/processes/{process_id}/performanceAdvisor/slowQueryLogs'''
        kwargs = {'auth': HTTPDigestAuth(config['username'], config['api_key']), "params": {
             "since": since, "duration": duration
        }}
        data = getdata(url, **kwargs)
        for ns in data['slowQueries']:
            ns['project_id'] = config['project_id']
            ns['process_id'] = process_id
            ns['timestamp'] = start_time_epoch
            sq_logs.append(ns)

    yamlconfig['SumoLogic']["SUMO_ENDPOINT"] = yamlconfig['SumoLogic']["LOGS_SUMO_ENDPOINT"]
    output_handler = OutputHandlerFactory.get_handler(yamlconfig['Collection']['OUTPUT_HANDLER'], path="%s.json" % "slow_query_lines", config=yamlconfig)
    send_success = output_handler.send(sq_logs)
    print(send_success)

    return sq_logs


def get_suggested_indexes_from_processes(config, process_ids, start_time_epoch, end_time_epoch):
    # Get Suggested Indexes
    since = start_time_epoch*1000
    duration = (end_time_epoch - start_time_epoch)*1000 # in ms
    si_logs = {}

    for process_id in process_ids:
        url = f'''{config['baseurl']}/groups/{config['project_id']}/processes/{process_id}/performanceAdvisor/suggestedIndexes'''
        kwargs = {'auth': HTTPDigestAuth(config['username'], config['api_key']), "params": {
             "since": since, "duration": duration
        }}
        data = getdata(url, **kwargs)
        print(data)
        for sidx in data['suggestedIndexes']:
            namespace = sidx.pop('namespace')
            if namespace not in si_logs:
                si_logs[namespace] = {
                    "suggestedIndexes": [], "operations": [], "project_id": config['project_id'],
                    'process_id': process_id, 'timestamp': start_time_epoch, "namespace": namespace
                }

            si_logs[namespace]["suggestedIndexes"].append(sidx)
        for shape in data['shapes']:
            namespace = shape.pop('namespace')
            if namespace in si_logs:
                for ops in si_logs[namespace]["operations"]:
                    ops["avgMs"] = shape["avgMs"]
                    ops["shape_id"] = shape["id"]
                    ops["inefficiencyScore"] = shape["inefficiencyScore"]
                    si_logs[namespace]["operations"].append(ops)

    suggested_indexes_logs = [v for k, v in si_logs.items()]
    yamlconfig['SumoLogic']["SUMO_ENDPOINT"] = yamlconfig['SumoLogic']["LOGS_SUMO_ENDPOINT"]
    output_handler = OutputHandlerFactory.get_handler(yamlconfig['Collection']['OUTPUT_HANDLER'], path="%s.json" % "suggested_indexes_logs", config=yamlconfig)
    send_success = output_handler.send(suggested_indexes_logs)
    print(send_success)

    return


# Events
def get_events_from_project(config, start_time_date, end_time_date):
    # Get all events for the project associated with {GROUP-ID}.
    event_logs = []
    url = f'''{config['baseurl']}/groups/{config['project_id']}/events'''
    kwargs = {
        'auth': HTTPDigestAuth(config['username'], config['api_key']),
        "params": {"itemsPerPage": 500, "minDate": start_time_date , "maxDate": end_time_date}
    }
    all_data = getpaginateddata(url, **kwargs)
    event_logs.extend([obj for data in all_data for obj in data['results']])
    yamlconfig['SumoLogic']["SUMO_ENDPOINT"] = yamlconfig['SumoLogic']["LOGS_SUMO_ENDPOINT"]
    output_handler = OutputHandlerFactory.get_handler(yamlconfig['Collection']['OUTPUT_HANDLER'], path="%s.json" % "suggested_indexes_logs", config=yamlconfig)

    send_success = output_handler.send(event_logs, extra_headers={'X-Sumo-Name': "events"})
    print(send_success)

    return event_logs


def get_events_from_org(config, start_time_date, end_time_date):
    event_logs = []
    url = f'''{config['baseurl']}/orgs/{config['org_id']}/events'''
    kwargs = {
        'auth': HTTPDigestAuth(config['username'], config['api_key']),
        "params": {"itemsPerPage": 500, "minDate": start_time_date , "maxDate": end_time_date}
    }
    all_data = getpaginateddata(url, **kwargs)
    event_logs.extend([obj for data in all_data for obj in data['results']])
    yamlconfig['SumoLogic']["SUMO_ENDPOINT"] = yamlconfig['SumoLogic']["LOGS_SUMO_ENDPOINT"]
    output_handler = OutputHandlerFactory.get_handler(yamlconfig['Collection']['OUTPUT_HANDLER'], path="%s.json" % "suggested_indexes_logs", config=yamlconfig)

    send_success = output_handler.send(event_logs, extra_headers={'X-Sumo-Name': "orgevents"})
    print(send_success)

    return event_logs


# Alerts
def get_alerts_from_project(config):
    # Get All Alerts
    alert_logs = []

    url = f'''{config['baseurl']}/groups/{config['project_id']}/alerts'''
    kwargs = {
        'auth': HTTPDigestAuth(config['username'], config['api_key']),
        "params": {"itemsPerPage": 500}#, "status": "OPEN"}
    }
    all_data = getpaginateddata(url, **kwargs)
    alert_logs.extend([obj for data in all_data for obj in data['results']])
    yamlconfig['SumoLogic']["SUMO_ENDPOINT"] = yamlconfig['SumoLogic']["LOGS_SUMO_ENDPOINT"]
    output_handler = OutputHandlerFactory.get_handler(yamlconfig['Collection']['OUTPUT_HANDLER'], path="%s.json" % "suggested_indexes_logs", config=yamlconfig)

    send_success = output_handler.send(alert_logs, extra_headers={'X-Sumo-Name': "alerts"})
    print(send_success)


    return alert_logs



if __name__ == '__main__':

    config = {
        "project_id": "5cd0343ff2a30b3880beddb0",
        # "api_key": "706e68f8-a49e-4c3b-9fe1-ab91adf44ef5",
        "api_key": "c873a343-f3e2-4fc5-8581-867baa6e5fe0",
        # "username": "hpal@sumologic.com",
        "username": "hpgstoga",
        "baseurl": "https://cloud.mongodb.com/api/atlas/v1.0",
        "org_id": "5cd0343ef2a30b3bc7b8f88e"
    }
    end_time_epoch = int(get_current_timestamp()) - 2*60
    start_time_epoch = end_time_epoch - 4*24*60*60
    process_ids, hostnames = get_all_processes_from_project(config)
    # database_names = get_all_databases(config, process_ids)
    # disks = get_all_disks_from_host(config, process_ids)
    print(process_ids)
    print(hostnames)
    # print(database_names)
    # print(disks)
    isoformat = '%Y-%m-%dT%H:%M:%S.%fZ'

    # process_metrics = get_process_metrics(config, process_ids, convert_epoch_to_utc_date(start_time_epoch, date_format=isoformat), convert_epoch_to_utc_date(end_time_epoch, date_format=isoformat))
    # # print(process_metrics)

    # database_metrics = get_database_metrics(config, process_ids, database_names, convert_epoch_to_utc_date(start_time_epoch, date_format=isoformat), convert_epoch_to_utc_date(end_time_epoch, date_format=isoformat))
    # # print(database_metrics)


    # disk_metrics = get_disk_metrics(config, process_ids, disks, convert_epoch_to_utc_date(start_time_epoch, date_format=isoformat), convert_epoch_to_utc_date(end_time_epoch, date_format=isoformat))
    # # print(disk_metrics)


    # sq_namespaces = get_slow_query_namespaces_from_process(config, process_ids, start_time_epoch, end_time_epoch)
    # # print(sq_namespaces)

    # sq_logs = get_slow_queries_from_process(config, process_ids, start_time_epoch, end_time_epoch)
    # # print(sq_logs)

    # si_logs = get_suggested_indexes_from_processes(config, process_ids, start_time_epoch, end_time_epoch)
    # print(si_logs)

    # event_logs = get_events_from_project(config, convert_epoch_to_utc_date(start_time_epoch, date_format=isoformat), convert_epoch_to_utc_date(end_time_epoch, date_format=isoformat))
    # # print(event_logs)

    # event_logs = get_events_from_org(config, convert_epoch_to_utc_date(start_time_epoch, date_format=isoformat), convert_epoch_to_utc_date(end_time_epoch, date_format=isoformat))
    # # print(event_logs)

    # alert_logs = get_alerts_from_project(config)
    # print(alert_logs)

    db_logs = get_logs_from_host(config, hostnames, start_time_epoch, end_time_epoch)
    # print(db_logs)





