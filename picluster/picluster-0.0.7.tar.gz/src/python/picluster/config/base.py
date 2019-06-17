class Config:
    APP_NAME = "dxcluster"
    ADMIN_NAME = "administrator"


# class WebConfig(Config):
#     DEBUG = True
#
#     POSTGREST_IP = "202.120.1.61"
#     POSTGREST_PORT = "3000"
#
#     POSTGREST_RPC_URL = f"http://{POSTGREST_IP}:{POSTGREST_PORT}/rpc/"


class DBConfig(Config):
    DEBUG = True
    TESTING = True

    FORTRESS_IP = "52.83.226.226"
    FORTRESS_SSH_PORT = 22
    FORTRESS_USER = "ec2-user"
    FORTRESS_SSH_PRI_KEY = "/mnt/users/qinglong/qinglong.pem"

    LOCAL_BIND_IP = "192.168.1.185"
    LOCAL_BIND_PORT = 65432

    DB_USER = "postgres"
    DB_PASSWD = "postgres"
    DB_IP = "postgres.cjyyxyz76ycw.rds.cn-northwest-1.amazonaws.com.cn"
    DB_NAME = "taskdb"
    DB_PORT = 5432


class GraphQLConfig(Config):
    GraphQL_IP = "52.83.226.226"
    GraphQL_PORT = 8088

    GraphQL_URL = f"http://{GraphQL_IP}:{GraphQL_PORT}/v1alpha1/graphql"


class ConfigFile(Config):
    FileName = "dxclusterConf.yaml"
    CwdConf = "./" + FileName
