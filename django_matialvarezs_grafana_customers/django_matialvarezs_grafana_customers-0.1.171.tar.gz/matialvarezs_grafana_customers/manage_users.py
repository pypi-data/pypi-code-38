from . import api, models, manage_organisations, utils


def create_user_and_add_to_organisation(django_user_project_id, username, email, name, password,
                                        object_organisation_project_id, organisation_id,**options):
    swith_to_current_org =options.get("swith_to_current_org",False)
    res_data = api.create_global_user(username, email, name, password)
    if res_data:
        grafana_user_id = res_data['id']
        django_grafana_user = utils.get_or_none_user_grafana(user_project_id=django_user_project_id,
                                                             grafana_user_id=grafana_user_id)
        if not django_grafana_user:
            django_grafana_user = models.DjangoGrafanaUser(user_project_id=django_user_project_id,
                                                           grafana_user_id=grafana_user_id)
            django_grafana_user.save()
            if swith_to_current_org:
                manage_organisations.change_current_organization(object_organisation_project_id, organisation_id)
            api.add_global_user_to_organisation(email)
            #res = api.delete_user_in_organisation(1, grafana_user_id)
            #print("RES AL ELIMINAR USUARIO DE ORG",res)
        return True
    else:
        return None


def create_user(django_user_project_id, username, email, name, password):
    res_data = api.create_global_user(username, email, name, password)
    if res_data:
        grafana_user_id = res_data['id']
        django_grafana_user = utils.get_or_none_user_grafana(user_project_id=django_user_project_id,
                                                             grafana_user_id=grafana_user_id)
        if not django_grafana_user:
            django_grafana_user = models.DjangoGrafanaUser(user_project_id=django_user_project_id,
                                                           grafana_user_id=grafana_user_id)
            django_grafana_user.save()
            res = api.delete_user_in_organisation(1, grafana_user_id)
            print("RES AL ELIMINAR USUARIO DE ORG", res)
        return True
    return False


def add_user_to_organisation(user_email, object_organisation_project_id, organisation_id):
    manage_organisations.change_current_organization(object_organisation_project_id, organisation_id)
    api.add_global_user_to_organisation(user_email)
