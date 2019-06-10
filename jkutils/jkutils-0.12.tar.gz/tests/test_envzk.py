from jkutils.env import EnvZk


# @pytest.mark.skip(reason="skip")
def test_new():
    ez = EnvZk("127.0.0.1:2181", "chaos", "localhost:12345",config_path="/entry/config/service")

    ez.init_conf("CUR_ENV", force=False)
    ez.init_conf("CHAOS_DB", force=False)
    ez.init_conf("SENTRY_URL")
    ez.init_conf("REDIS_URL", force=False)
    ez.init_conf("LOG_DB", force=False)
    ez.init_conf("SQLALCHEMY_TRACK_MODIFICATIONS", default=False, conftype=bool)
    ez.init_conf("SQLALCHEMY_POOL_SIZE", default=5, conftype=int)
    ez.init_conf("ALERT_SENTRY_DNS")
    ez.init_conf("SMS_SENDING_LIMIT", default=100, conftype=int)
    ez.init_conf("VERIFY_CODE_EXPIRE", default=2, conftype=int)
    ez.init_conf("VERIFY_CODE_EXPIRE_MAIL", default=5, conftype=int)
    ez.init_conf("AMAP_SERVICE_KEY", force=False)
    ez.init_conf("IPV4_DATX_URL", force=False)
    ez.init_conf("MONGO_URI", default="ssssss", force=True)
    ez.init_conf("IS_SEND_SMS", default=True, conftype=bool)
    ez.init_conf("bool_test", default="False", conftype=bool)

    def handle_list(src):
        import json

        return json.loads(src)

    ez.init_conf("test_list", default='["aaa", "bbb"]', pre_use=handle_list)

    # 动态获取
    # 拿不到返回 None
    assert ez["REPORT_EXC_URL"] is None
    assert ez["test_list"] == ["aaa", "bbb"]


def test_one():
    ez = EnvZk("127.0.0.1:2181", "chaos", "localhost:12345")

    ez.init_conf("CUR_ENV", force=False)
    ez.init_conf("CHAOS_DB", force=False)
    ez.init_conf("SENTRY_URL")
    ez.init_conf("REDIS_URL", force=False)
    ez.init_conf("LOG_DB", force=False)
    ez.init_conf("SQLALCHEMY_TRACK_MODIFICATIONS", default=False, conftype=bool)
    ez.init_conf("SQLALCHEMY_POOL_SIZE", default=5, conftype=int)
    ez.init_conf("ALERT_SENTRY_DNS")
    ez.init_conf("SMS_SENDING_LIMIT", default=100, conftype=int)
    ez.init_conf("VERIFY_CODE_EXPIRE", default=2, conftype=int)
    ez.init_conf("VERIFY_CODE_EXPIRE_MAIL", default=5, conftype=int)
    ez.init_conf("AMAP_SERVICE_KEY", force=False)
    ez.init_conf("IPV4_DATX_URL", force=False)
    ez.init_conf("MONGO_URI", default="ssssss", force=True)
    ez.init_conf("IS_SEND_SMS", default=True, conftype=bool)
    ez.init_conf("bool_test", default="False", conftype=bool)

    def handle_list(src):
        import json

        return json.loads(src)

    ez.init_conf("test_list", default='["aaa", "bbb"]', pre_use=handle_list)

    # 动态获取
    # 拿不到返回 None
    assert ez["REPORT_EXC_URL"] is None
    assert ez["test_list"] == ["aaa", "bbb"]