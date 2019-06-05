from . import api, models, utils


def create_organisation(object_project_id, name):
    res_data = api.create_organisation(name)
    if res_data:
        org = utils.get_or_none_organisation_grafana(object_project_id=object_project_id,organisation_id=res_data['orgId'])
        if not org:
            utils.create_organisation_grafana(object_project_id=object_project_id, organisation_id=res_data['orgId'])
            return res_data['orgId']
    else:
        return None
            # customer_org_grafana = models.OrganisationGrafana(object_project_id=object_project_id,
            #                                                   organisation_id=res_data['orgId'])
            # customer_org_grafana.save()


def change_current_organization(object_project_id,organisation_id):
    organisation = models.OrganisationGrafana.objects.get(object_project_id=object_project_id,organisation_id=organisation_id)
    api.change_current_organization(organisation.organisation_id)


def update_organisation():
    pass
