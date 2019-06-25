from datetime import datetime

from requests.auth import AuthBase

from config.annotation import Value


# region 从配置文件中读取是否开启认证的配置
@Value("${sobeycube.oauth.enable:False}")
def enableOauth2():
    pass


@Value("${sobeycube.oauth.client_id:}")
def application_key():
    pass


@Value("${sobeycube.oauth.client_secret:}")
def secret_key():
    pass


@Value("${sobeycube.oauth.username:}")
def user_name():
    pass


@Value("${sobeycube.oauth.password:}")
def user_password():
    pass


# endregion

# region oauth2的认证
access_token = None
oauth_expiration: datetime = None


def acquire_access_token():
    """
    重新申请accessToken
    :return:
    """
    from client import AuthClient
    token, expiration = AuthClient.oauth_access_token(application_key(), secret_key())

    global access_token
    access_token = token

    global oauth_expiration
    oauth_expiration = expiration

    return access_token


def get_oauth_token():
    """
    生成oauth2的token
    :return:
    """

    global access_token
    if access_token is None or (oauth_expiration is not None and oauth_expiration <= datetime.now()):
        #  说明没有token, 或者token过期了
        access_token = acquire_access_token()

    return access_token


def _extract_auth_str(tokenType):
    """
    返回oauth的token
    :param tokenType:
    :return:
    """
    return f"{tokenType} {get_oauth_token()}"


# endregion

# region JWT的认证
jwt_token = None
jwt_expiration: datetime = None


def acquire_jwt_token():
    """
    重新申请jwtToken
    :return:
    """
    from client import AuthClient
    token, expiration = AuthClient.oauth_jwt_token(user_name(), user_password())
    jwt_token = token

    global jwt_expiration
    jwt_expiration = expiration

    return jwt_token


def _extract_jwt_str():
    global jwt_token
    if jwt_token is None or (jwt_expiration is not None and jwt_expiration <= datetime.now()):
        #  说明没有token, 或者token过期了
        jwt_token = acquire_jwt_token()

    return jwt_token


# endregion

class ClientAuth(AuthBase):
    """
    自定义的client认证
    """

    def __call__(self, r):
        """
        必须实现的这个方法,类似于JAVA中的 filter. 在调用的的时候增加认证的东西
        :param r: PreparedRequest实例
        :return:
        """

        if enableOauth2() == False:
            # 如果没有打开认证,就直接返回
            return r

        # 如果是开启了认证的,就需要提供两个认证,一个是oauth2,一个是jwt的

        # 先校验oauth2的
        r.headers['Authorization'] = _extract_auth_str("Bearer")

        # 再处理jwt的认证
        if user_name() is not None and user_password() is not None:
            # 开启了认证,并且填写了userName和password.才增加这个请求头
            r.headers['sobeycube-http-token'] = _extract_jwt_str()

        return r
