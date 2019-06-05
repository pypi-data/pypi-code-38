from django.db.models import Q

from . import api, models,utils


def create_folder(name,**options):
    object_project_id = options.get('object_project_id',0)
    res = api.create_folder(name)
    if res:
        folder = utils.get_or_none_folder_grafana(object_project_id=object_project_id)
        if not folder:
            folder = models.FolderGrafana(folder_id=res['id'], folder_uid=res['uid'], name=name,object_project_id=object_project_id)
            folder.save()
        return True
    else:
        return False


def update_folder(name, **options):
    folder_uid = options.get('folder_uid','')
    object_project_id = options.get('object_project_id',0)
    folder = models.FolderGrafana.objects.get(Q(folder_uid=folder_uid) | Q(object_project_id=object_project_id))
    res = api.update_folder(name, folder.folder_uid)
    if res:
        #
        folder.name = name
        folder.save()
        return folder
    else:
        return None

def delete_folder(folder_uid):
    return api.delete_folder(folder_uid)