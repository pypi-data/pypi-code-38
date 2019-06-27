"""
认证模块操作
"""
import requests
from munch import Munch

from api.exceptions import IllegalArgumentException
from client import do_service, check_instance_avaliable


def get_authorization_header(client_id, client_secret):
    import base64
    return f"Basic {str(base64.b64encode(f'{client_id}:{client_secret}'.encode('utf-8')))}"


def oauth_access_token(server, grant_type, client_id, client_secret, username, password):
    """
    获取oauth系统认证的accessToken
    :param client_id:
    :param client_secret:
    :return:
    """
    check_instance_avaliable()

    try:
        r = do_service(
            f"/oauth/token?grant_type={grant_type}&scope=all&username={username}&password={password}"
            , app_name=server, method="POST", auth=None,
            headers={"Authorization": get_authorization_header(client_id, client_secret)})

        if r is not None:
            entity = Munch(r)

            from datetime import datetime
            import time
            return entity["access_token"], datetime.fromtimestamp(time.time() + entity["expires_in"])
        else:
            return None, None
    except requests.exceptions.HTTPError as ee:
        raise IllegalArgumentException(f"从ficus获取oauth签名失败,{ee.response.status_code}")


def oauth_jwt_token(user_name, user_password):
    """
    获取jwt的用户内容权限的jwtToken
    :param user_name:
    :param user_password:
    :return:
    """

    check_instance_avaliable()

    try:
        r = do_service("/user/login", method="POST", return_type="str",
                       data={"username": user_name, "password": user_password}, auth=None)

        if r is not None:
            jwt_token = r
            return (jwt_token, _find_expiration(jwt_token))
        else:
            return (None, None)
    except requests.exceptions.HTTPError as ee:
        raise IllegalArgumentException(f"从ficus获取用户认证失败,{ee.response.status_code}")


def _find_expiration(jwt_token: str):
    """
    解析jwtToken的过期时间
    :param jwt_token:
    :return:
    """

    # jwt有三部分,每个部分用逗号分隔.
    if jwt_token is None:
        return None

    splits = jwt_token.split(".")

    # 取第二部分
    s = splits[1]

    # 把第二部分用base64解码.
    import base64
    s1 = base64.b64decode(s)

    # 出来是一个map,取exp字段
    import json
    json_object = json.loads(s1)

    exp = json_object["exp"]

    from datetime import datetime
    return datetime.fromtimestamp(exp)
