import json

from django.conf import settings
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .utils import apply_update


@csrf_exempt
def update(request):
    if "data" not in request.POST:
        return JsonResponse(
            {"error": "Неправильный формат запроса"},
            status=422
        )
    if "HTTP_AUTHORIZATION" not in request.META:
        return JsonResponse(
            {"error": "Требуется авторизация"},
            status=403
        )

    auth = request.META["HTTP_AUTHORIZATION"]
    required_auth = "Bearer {}".format(settings.GLOSSARY_SERVICE_TOKEN)
    if auth != required_auth:
        return JsonResponse({"error": "Неверный токен"}, status=403)

    data = json.loads(request.POST["data"])
    try:
        apply_update(data)
    except BaseException as e:
        return JsonResponse({"error": str(e)}, status=500)

    return HttpResponse()
