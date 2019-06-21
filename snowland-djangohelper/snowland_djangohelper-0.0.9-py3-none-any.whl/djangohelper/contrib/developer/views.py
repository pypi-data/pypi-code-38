from django.contrib.auth import authenticate
from django.http import JsonResponse
from pysmx.SM2 import generate_keypair
from pysmx.SM3 import SM3
from djangohelper.developer.models import *
from datetime import datetime
from django.forms.models import model_to_dict
from djangohelper.common import (
    JSON_DEMO, ERROR_CODE_PARTNER_ERROR, ERROR_CODE_UNKNOWN
)

@authenticate
def new_application(req):
    result = JSON_DEMO.copy()
    try:
        if req.method == 'POST':
            user = req.user
            name = req.POST.get('name', None)
            icon = req.POST.get('icon', None)
            assert user or name
            keypair = generate_keypair()
            sm3 = SM3()
            timestamp = str(datetime.now())
            sm3.update(name+'$'+timestamp)
            app = Application.objects.create(
                owner=user,
                name=name,
                access_key=keypair.publicKey,
                access_secret=keypair.privateKey,
                icon=icon
            )
            KeyStore.objects.create(
                app_id=app,
                public_key=keypair.publicKey,
            )
            result['data'] = model_to_dict(app, ['access_key', 'app.access_key', 'name'])
            return JsonResponse(result)
        else:
            result['successful'] = False
            result['code'] = ERROR_CODE_PARTNER_ERROR,
            result['message'] = '该方法需要post请求'
            return JsonResponse(result)
    except:
        result['successful'] = False
        result['code'] = ERROR_CODE_UNKNOWN,
        result['message'] = '未知错误'
        return JsonResponse(result)


@authenticate
def change_key(req):
    result = JSON_DEMO.copy()
    try:
        if req.method == 'POST':
            user = req.user
            app_id = req.POST.get('app_id', None)
            assert user or app_id
            keypair = generate_keypair()
            app = Application.objects.get(app_id=app_id)
            ApplicationChangeList.object.create(
                app_id=app,
                access_secret_before=app.access_secret,
                access_secret_after=keypair.privateKey,
                access_key_before=app.access_key,
                access_key_after=keypair.publicKey,
            )
            KeyStore.object.create(
                app_id=app,
                public_key=keypair.publicKey,
            )
            app.access_secret = keypair.privateKey
            app.access_key=keypair.publicKey
            app.save()
            result['data'] = app.__dict__()
            return JsonResponse(result)
        else:
            result['successful'] = False
            result['code'] = ERROR_CODE_PARTNER_ERROR,
            result['message'] = '该方法需要post请求'
            return JsonResponse(result)
    except:
        result['successful'] = False
        result['code'] = ERROR_CODE_UNKNOWN,
        result['message'] = '未知错误'
        return JsonResponse(result)