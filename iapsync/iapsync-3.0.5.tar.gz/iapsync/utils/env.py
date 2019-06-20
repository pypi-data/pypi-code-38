import re

IELTS_LIVE_TEST = re.compile('live\.')
def get_api_env(env_or_product_id):
    ''' product_id的格式是"${env}.id" '''
    api_env=env_or_product_id.split('.')[0]
    # 历史原因，有两个app的'env'字段的格式不是"api_env.app_name"的格式：名师课app(api_env)，斩雅思app(live, dev.live)
    if api_env not in ['dev', 'sim', 'prod']:
        if env_or_product_id == 'live' or IELTS_LIVE_TEST.match(env_or_product_id):
            api_env = 'prod'
        else:
            raise ValueError("参数不合法：%s" % env_or_product_id)
    return api_env
