
import time
import datetime
import os

from elasticsearch import Elasticsearch


SEARCH_DATA_PATTERN_ES_V5 = {
    "query": {
        "bool": {
            "filter": {
                "bool": {
                    "must": [
                        {
                            "query_string": {
                                "query": ""
                            }
                        },
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": "",
                                    "lte": ""
                                }
                            }
                        }
                    ]
                }
            }
        }
    }
}
SERVER_DELTA = datetime.timedelta(hours=3)  # разница с сервером
TEST_PROJECT = os.environ.get('TEST_PROJECT')
ELASTICSEARCH_HOST = 'es-kibana.olympus.evo:9250'
KIBANA_DOMAIN = "kibana.olympus.evo"
LEVELS_SEARCH_STR = (
    "(level:\"ERROR\" OR level:\"CRITICAL\""
    " OR level:\"err\" OR level:\"FATAL\" OR level:\"crit\""
    " OR http_status:>=500)"
)
LEVELS_URL_STR = (
    "%28level:ERROR%20OR"
    "%20level:CRITICAL%20OR"
    "%20level:err%20OR"
    "%20level:FATAL%20OR"
    "%20level:crit%20OR"
    "%20http_status:%3E%3D500%29"
)
BASE_QUERY_STR = f"{LEVELS_SEARCH_STR}"
BASE_KIBANA_URL_PATTERN = (
    "https://{domain}/#/discover?_g=%28refreshInterval:"
    "%28display:Off,pause:!f,section:0,value:0%29,time:%28from:%27{time_from}"
    ".000Z%27,mode:absolute,to:%27{time_to}"
    ".000Z%27%29%29&_a=%28columns:!%28_source%29,index:%27logstash-%2A%27,"
    "interval:auto,query:%28query_string:%28analyze_wildcard:!t,"
    "query:%27{query}%20%27%29%29,sort:!%28%27@timestamp%27,desc%29%29"
)


def get_all_logs_link_by_xrequestid(xrequestid):
    return (
        f"https://kibana.olympus.evo/app/kibana#/discover?"
        f"_g=%28refreshInterval:%28display:Off%2Cpause:!f%2Cvalue:0%29%2C"
        f"time:%28from:now-1h%2Cmode:quick%2Cto:now%29%29&"
        f"_a=%28columns:!%28level%2Cservice%2Cmessage%2Cexception.tb"
        f"%2Chttp_status%29%2Cfilters:!%28%29%2Cindex:%27logstash-*%27%2C"
        f"interval:auto%2Cquery:%28query_string:%28analyze_wildcard:!"
        f"t%2Cquery:%22{xrequestid}%22%29%29%2C"
        f"sort:!%28%27@timestamp%27%2Cdesc%29%29"
    )


def connect_to_es_and_get_search_result(data):
    es = Elasticsearch(hosts=[ELASTICSEARCH_HOST])
    result = es.search(
        index='logstash-*',
        body=data, size=10
    )
    return result


def set_search_data(query_string, t_from, t_to):
    data = SEARCH_DATA_PATTERN_ES_V5
    must = data["query"]["bool"]["filter"]["bool"]["must"]
    must[0]["query_string"]["query"] = query_string
    must[1]["range"]["@timestamp"]["gte"] = t_from
    must[1]["range"]["@timestamp"]["lte"] = t_to
    return data


def wait_for_kibana_search_result(data):
    attempts = 16  # 8 seconds
    while attempts:
        result = connect_to_es_and_get_search_result(data)
        hits = result['hits']['hits']
        if hits:
            return result
        time.sleep(.5)
        attempts -= 1
    return None


def get_error_message(hit):
    source = hit["_source"]
    if source['service'] == "postgres" and "query" in source:
        return (
            f"MESSAGE: {source['message']}"
            f"\nDATABASE: {source['database']}"
            f"\nQUERY: {source['query']}"
        )
    if "exception" in source:
        return(
            f"SERVICE: {source.get('service')}"
            f"\nEXCEPTION VALUE:\n\t{source['exception'].get('value')}"
            f"\nEXCEPTION TRACEBACK:\n\t{source['exception'].get('tb')}"
        )
    if "message" in source:
        return (
            f"SERVICE: {source.get('service')}"
            f"\nMESSAGE:\n\t{source['message']}"
        )
    if "http_host" in source and "request" in source:
        return ("STATUS CODE: %s - %s" % (
            source["http_status"],
            source["http_host"] + source["request"]
        ))
    return f"{source}"


def get_kibana_link_for_one_test(xrequestid):
    try:
        time_from = datetime.date.today().strftime("%Y-%m-%d")
        time_to = (
            datetime.date.today() + datetime.timedelta(days=1, hours=3)
        ).strftime("%Y-%m-%d")
        query = f"txid:%22{xrequestid}%22%20AND%20{LEVELS_URL_STR}"
        kibana_pattern = BASE_KIBANA_URL_PATTERN.format(
            query=query,
            time_from=time_from + "T00:00:00",
            time_to=time_to + "T00:00:00",
            domain=KIBANA_DOMAIN
        )
        today = datetime.date.today().strftime("%Y-%m-%d")
        query_string = f"txid:\"{xrequestid}\" AND {BASE_QUERY_STR}"
        data = set_search_data(
            query_string,
            f"{today}T00:00:00.000Z",
            f"{today}T23:59:59.000Z"
        )
        result = connect_to_es_and_get_search_result(data)
        hits = result['hits']['hits']
        if hits:
            tbs = list(set(map(
                lambda x: get_error_message(x),
                result['hits']['hits'])
            ))
            return (
                "by x-request-id",
                kibana_pattern,
                result['hits']['total'],
                tbs
            )
    except Exception as e:
        print("Something wrong: %s" % repr(e))


def _save_variable_to_properties_file(var):
    """ Use method for Jenkins only """
    IS_JENKINS_BUILD = os.environ.get("IS_JENKINS_BUILD")
    print(os.environ)
    print("Is jenkins build?", IS_JENKINS_BUILD)
    if IS_JENKINS_BUILD == "true":
        file_name = "envVars.properties"
        f = open(file_name, "a")
        print(f)
        if (os.path.getsize(file_name) > 0):
            f.write("\n" + var)
        else:
            f.write(var)
        f.close()
    print("Done.")


def get_kibana_link_for_all_tests(start, stop):
    search_portal = TEST_PROJECT
    tags_query = search_portal
    tags_query_string = search_portal

    if 'trunk' in search_portal:
        search_portal = search_portal.replace('-', '')
    # TODO someday to do for all portals
    if 'madmax' in search_portal:
        tags_query = f"%28{search_portal}*%20AND%20NOT%20cms-ui%29"
        tags_query_string = f"({search_portal}* AND NOT cms-ui)"

    try:
        delta = SERVER_DELTA
        time_from = (start - delta).strftime("%Y-%m-%dT%H:%M:%S")
        time_to = (stop - delta).strftime("%Y-%m-%dT%H:%M:%S")
        query = (
            f"%28site:{search_portal}%20OR%20"
            f"service:%22prom-{search_portal}%22%20OR%20"
            f"tags:{tags_query}%29"
            f"%20AND%20{LEVELS_URL_STR}"
        )
        kibana_pattern = BASE_KIBANA_URL_PATTERN.format(
            query=query,
            time_from=time_from,
            time_to=time_to,
            domain=KIBANA_DOMAIN
        )
        print(kibana_pattern)
        query_string = (
            f"(site:{search_portal} OR service:\"prom-{search_portal}\""
            f" OR tags:{tags_query_string}) AND {BASE_QUERY_STR}"
        )
        data = set_search_data(
            query_string,
            f"{time_from}.000Z",
            f"{time_to}.000Z"
        )
        result = wait_for_kibana_search_result(data)
        if result:
            hits = result['hits']['hits']
            if hits:
                print("ALL APPLICATION ERRORS IN KIBANA:", kibana_pattern)
                print("\nFound errors in kibana.")
                print("\nTotal:", result['hits']['total'], "error(s)")
                _save_variable_to_properties_file(
                    f"KIBANA_URL={kibana_pattern}"
                )
        # TODO someday to do for all portals
        if 'madmax' in search_portal:
            cms_ui_url_query = (
                f"tags:%28{search_portal}*%20AND%20cms-ui%29%20AND%20level:err"
            )
            cms_ui_query_string = (
                f"tags:({search_portal}* AND cms-ui) AND level:err"
            )
            cms_ui_pattern = BASE_KIBANA_URL_PATTERN.format(
                query=cms_ui_url_query,
                time_from=time_from,
                time_to=time_to,
                domain=KIBANA_DOMAIN
            )
            print(f"CMS-UI URL: {cms_ui_pattern}")  # noqa
            cms_ui_data = set_search_data(
                cms_ui_query_string,
                f"{time_from}.000Z",
                f"{time_to}.000Z"
            )
            cms_ui_result = wait_for_kibana_search_result(cms_ui_data)
            if cms_ui_result:
                cms_ui_hits = cms_ui_result['hits']['hits']
                if cms_ui_hits:
                    _save_variable_to_properties_file(
                        f"CMS_UI_URL={cms_ui_pattern}"
                    )
        services_url_query = (
            "service:(%22adv-olympus%22"
            "%20OR%20(besida%20AND%20NOT%20stable)"
            "%20OR%20%22pixel-olympus%22"
            "%20OR%20%22search-autocomplete-olympus%22"
            "%20OR%20%22appstats-olympus%22"
            "%20OR%20%22susanin%2F{test_project}-app%22"
            ")%20AND%20level:%22err%22"
        )
        services_query_string = (
            'service:("adv-olympus"'
            ' OR (besida AND NOT stable)'
            ' OR "pixel-olympus"'
            ' OR "search-autocomplete-olympus"'
            ' OR "appstats-olympus"'
            ' OR "susanin/{test_project}-app"'
            ') AND level:"err"'
        )
        services_pattern = BASE_KIBANA_URL_PATTERN.format(
            query=services_url_query.format(test_project=search_portal),
            time_from=time_from,
            time_to=time_to,
            domain=KIBANA_DOMAIN
        )
        services_data = set_search_data(
            services_query_string.format(test_project=search_portal),
            f"{time_from}.000Z",
            f"{time_to}.000Z"
        )
        services_result = wait_for_kibana_search_result(services_data)
        if services_result:
            services_hits = services_result['hits']['hits']
            if services_hits:
                _save_variable_to_properties_file(
                    f"SERVICES_URL={services_pattern}"
                )
        return None

    except Exception as e:
        print("Something wrong: %s" % repr(e))
