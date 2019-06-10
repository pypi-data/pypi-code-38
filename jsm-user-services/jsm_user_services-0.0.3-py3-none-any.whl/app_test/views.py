from django.http import JsonResponse
from jsm_user_services.services.user import current_jwt_token
from jsm_user_services.services.user import get_jsm_token
from jsm_user_services.services.user import get_jsm_user_data_from_jwt
from jsm_user_services.services.user import get_ltm_token
from jsm_user_services.services.user import get_ltm_user_data_from_jwt
from jsm_user_services.services.user import get_user_email_from_jwt


def view_test(request):

    data = {
        "current_jwt_token": current_jwt_token(),
        "get_jsm_token": get_jsm_token(),
        "get_ltm_token": get_ltm_token(),
        "get_jsm_user_data_from_jwt": get_jsm_user_data_from_jwt(),
        "get_ltm_user_data_from_jwt": get_ltm_user_data_from_jwt(),
        "get_user_email_from_jwt": get_user_email_from_jwt(),
    }

    return JsonResponse(data)
