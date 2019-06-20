import json
from django.http import HttpResponse
from .backend import Progress
from django.core.serializers.json import DjangoJSONEncoder

def get_progress(request, task_id):
    progress = Progress(task_id)
    json_info_dumps = json.dumps(progress.get_info(), cls=DjangoJSONEncoder)
    return HttpResponse(json_info_dumps, content_type='application/json')
