from . import settings
from matialvarezs_request_handler import utils as matialvarezs_request_handler_utils
# from . import models
import json
from ohm2_handlers_light import utils as ohm2_handlers_light_utils


def create_organisation(name):
    data = {
        "name": name
    }
    res = matialvarezs_request_handler_utils.send_post_and_get_response(settings.GRAFANA_API_BASE_URL + 'orgs',
                                                                        data=data, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    # res = requests.post(settings.GRAFANA_API_BASE_URL + 'orgs',data=data, headers=settings.GRAFANA_API_HEADERS)
    # res.
    print("res antes de guardar organisation en grafana", res.content)
    if res.status_code == 200:
        print("res al guardar organisation en grafana", res.content)
        return json.loads(res.content.decode('utf-8'))
        # organisation_id = res_data['orgId']

    else:
        print("error al guardar organisation")
        return None


def update_organisation(object_project_id, name):
    pass


def change_current_organization(organisation_id):
    # organisation = models.OrganisationGrafana.objects.get(object_project_id=object_project_id)
    url = settings.GRAFANA_API_BASE_URL + 'user/using/' + str(organisation_id)
    res = matialvarezs_request_handler_utils.send_post_and_get_response(url,
                                                                        data={}, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    if res.status_code == 200:
        print("ORGANIZACION GRAFANA ACTUAL CAMBIADA")
    else:
        print("ERROR AL CAMBIAR ORGANIZACION ACTUAL GRAFANA")
    return res


def create_datasource_postgresql():
    data = {
        "name": settings.DATASOURCE_NAME,
        "type": "postgres",
        "access": "proxy",
        # "url": settings.DATABASE_HOST + ":" + settings.DATABASE_PORT,
        "url": settings.DATABASE_HOST,
        # "host":settings.DATABASE_HOST,
        # "port":settings.DATABASE_PORT,
        "secureJsonData": {
            "password": settings.DATABASE_PASSWORD
        },
        "user": settings.DATABASE_USER,
        "database": settings.DATABASE_NAME,
        "jsonData": {
            "host": settings.DATABASE_HOST,
            "port": settings.DATABASE_PORT,
            "sslmode": "disable",
            "default": True
        },

    }
    # organisation = models.OrganisationGrafana.objects.get(object_project_id=1)
    url = settings.GRAFANA_API_BASE_URL + 'datasources'
    res = matialvarezs_request_handler_utils.send_post_and_get_response(url,
                                                                        data=data, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    if res.status_code == 200:
        print("OK crear datasource")
    else:
        print("error al crear datasource")
        print(res.reason)


def create_datasource_influxdb(datasource_name, url, database_password, database_user, database_name, database_host,
                               database_port):
    data = {
        "name": datasource_name,
        "type": "influxdb",
        "access": "proxy",
        # "url": settings.DATABASE_HOST + ":" + settings.DATABASE_PORT,
        "url": url,
        # "host":settings.DATABASE_HOST,
        # "port":settings.DATABASE_PORT,
        "secureJsonData": {
            "password": database_password
        },
        "user": database_user,
        "database": database_name,
        "jsonData": {
            "host": database_host,
            "port": database_port,
            "sslmode": "disable",
            "default": True
        },

    }
    # organisation = models.OrganisationGrafana.objects.get(object_project_id=1)
    url = settings.GRAFANA_API_BASE_URL + 'datasources'
    res = matialvarezs_request_handler_utils.send_post_and_get_response(url,
                                                                        data=data, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    if res.status_code == 200:
        print("OK crear datasource")
    else:
        print("error al crear datasource")
        print(res.reason)
    return res


def create_folder(name):
    data = {
        "uid": None,
        "title": name
    }
    res = matialvarezs_request_handler_utils.send_post_and_get_response(settings.GRAFANA_API_BASE_URL + 'folders',
                                                                        data=data, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    if res.status_code == 200:
        return res.json()
    else:
        print("ERRROR ON CREATE FOLDER: ", res.status_code, res.reason)
        return None


def update_folder(name, folder_uid):
    data = {
        "title": name,
    }
    res = matialvarezs_request_handler_utils.send_put(settings.GRAFANA_API_BASE_URL + 'folders/' + folder_uid,
                                                      data=data, headers=settings.GRAFANA_API_HEADERS,
                                                      convert_data_to_json=True)
    return res


def delete_folder(folder_uid):
    res = matialvarezs_request_handler_utils.send_delete(settings.GRAFANA_API_BASE_URL + 'folders/' + folder_uid,
                                                         headers=settings.GRAFANA_API_HEADERS)
    return res


def restore_folder_permissions(folder_uid):
    url = settings.GRAFANA_API_BASE_URL + 'folders/' + folder_uid + '/permissions'
    data = {
        "items": [
            {
                "role": "Viewer",
                "permission": 1
            },
        ]
    }
    res = matialvarezs_request_handler_utils.send_post_and_get_response(url=url, data=json.dumps(data),
                                                                        headers=settings.GRAFANA_API_HEADERS)
    print(res.content, res.status_code, res.reason)


def remove_folder_perssions(folder_uid):
    url = settings.GRAFANA_API_BASE_URL + 'folders/' + folder_uid + '/permissions'
    data = {
        "items": [
            {
                "role": "Viewer",
                "permission": None
            },
        ]
    }
    res = matialvarezs_request_handler_utils.send_post_and_get_response(url=url, data=json.dumps(data),
                                                                        headers=settings.GRAFANA_API_HEADERS)
    print(res.content, res.status_code, res.reason)


def create_global_user(username, email, name, password):
    data = {
        "role": "Viewer",
        "loginOrEmail": username,
        "password": password,
        "email": email,
        "name": name

    }

    print(settings.GRAFANA_API_BASE_URL + 'admin/users')
    res = matialvarezs_request_handler_utils.send_post_and_get_response(settings.GRAFANA_API_BASE_URL + 'admin/users',
                                                                        data=data, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    print(res)
    if res.status_code == 200:
        print(res.json())
        print("USUARIO GRAFANA GUARDADO")
        return res.json()
    else:
        print("ERROR AL CREAR USUARIO", res.reason)
        return None


def add_global_user_to_organisation(email):
    data = {
        "role": "Viewer",
        "loginOrEmail": email
    }
    print("add_global_user_to_organisation url", settings.GRAFANA_API_BASE_URL + 'org/users')
    res = matialvarezs_request_handler_utils.send_post_and_get_response(settings.GRAFANA_API_BASE_URL + 'org/users',
                                                                        data=data, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    print("res al asociar usuario con organisacion actual", res)
    return res.status_code == 200


# settings.GRAFANA_API_BASE_URL + 'orgs/1/users/'+str(data['id']),
def delete_user_in_organisation(organisation_id, user_id):
    res = matialvarezs_request_handler_utils.send_delete(
        settings.GRAFANA_API_BASE_URL + 'orgs/' + str(organisation_id) + '/users/' + str(user_id),
        headers=settings.GRAFANA_API_HEADERS)
    return res


def get_dashboard_by_uid(dashboard_uid):
    res = matialvarezs_request_handler_utils.send_get_and_get_response(
        settings.GRAFANA_API_BASE_URL + 'dashboards/uid/' + dashboard_uid)
    if res.status_code == 200:

        print("RES AL GET DASHBOARD", json.loads(res.content.decode('utf-8')))
        res_data = json.loads(res.content.decode('utf-8'))
        return res_data


    else:
        print("ERROR AL GET DASHBOARD", json.loads(res.content.decode('utf-8')), res.reason)
        return None


def create_dashboard(dashboard, **options):
    title = options.get('title', ohm2_handlers_light_utils.random_string(8))
    folder_id = options.get("folder_id",0)
    panels = options.get("panels",False)
    data = {
        "dashboard": {
            "id": None,
            "uid": None,
            "title": title,
            # "tags": ["templated"],
            "timezone": "browser",
            "schemaVersion": 16,
            "version": 0
        },
        "folderId": folder_id,
        "overwrite": False
    }
    if panels:
        data['dashboard']['panels'] = []
    folder_id = options.get('folder_id', 0)
    # data = {
    #     "dashboard": dashboard.dashboard_content,
    #     "folderId": folder_id,
    #     "overwrite": False
    # }

    res = matialvarezs_request_handler_utils.send_post_and_get_response(settings.GRAFANA_API_BASE_URL + 'dashboards/db',
                                                                        data=data, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    print("***** DATA AL GUARDAR DASHBOARD ", data)
    if res.status_code == 200:

        print("RES AL GUARDAR DASHBOARD", json.loads(res.content.decode('utf-8')))
        res_data = json.loads(res.content.decode('utf-8'))
        return res_data


    else:
        print("ERROR AL GUARDAR DASHBOARD", json.loads(res.content.decode('utf-8')), res.reason)
        return None


def update_dashboard(json_dashboard, folder_id):
    data = {
        "dashboard": json_dashboard,
        "folderId": folder_id,
        "overwrite": True,
    }
    res = matialvarezs_request_handler_utils.send_post_and_get_response(settings.GRAFANA_API_BASE_URL + 'dashboards/db',
                                                                        data=data, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    if res.status_code == 200:
        # dashboard_db_storaged.dashboard_content = json_dashboard
        # dashboard_db_storaged.save()
        print("**** DATA AL ACTUALIZAR DASHBOARD ****", data)
        print("RES AL ACTUALIZAR DASHBOARD", json.loads(res.content.decode('utf-8')))
    else:
        print("ERROR AL ACTUALIZAR DASHBOARD", json.loads(res.content.decode('utf-8')), res.reason)


def delete_dashboard(dashboard_uid):
    res = matialvarezs_request_handler_utils.send_delete(
        settings.GRAFANA_API_BASE_URL + 'dashboards/uid/' + dashboard_uid,
        headers=settings.GRAFANA_API_HEADERS)
    # print(res,res.status_code,res.reason)
    return res
