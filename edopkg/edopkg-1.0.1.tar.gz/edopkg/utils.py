# encoding: utf-8

from edo_client import OcClient, WoClient

def get_wo_client(oc_api, client_id, client_secret, account, instance, username, password):
    # 连接应用服务器
    print u' 正在连接到服务器... 地址：%s '% oc_api
    oc_client= OcClient(oc_api, client_id, client_secret,
            account = account)

    #  获取认证
    print u' 正在获取服务器认证... 账号：%s ' % account
    oc_client.auth_with_password(username=username,
            password=password, account=account)

    #  获取服务
    print u' 正在获取云办公服务... 站点：%s ' % instance
    wo_instance = oc_client.account.get_instance(account=account,
            application='workonline', instance=instance)
    print u'wo_api地址为: ', wo_instance['api_url']

    #  获取连接
    wo_client = WoClient(wo_instance['api_url'], client_id,
            client_secret, account=account, instance=instance)

    #  获取认证
    wo_client.auth_with_token(oc_client.access_token)
    print u' 成功获取连接： %(oc_api)s, 账号 %(account)s, 站点 %(instance)s ' % {
        'oc_api':oc_api,
        'account':account,
        'instance':instance
    }
    return wo_client

def complie_script(script):
   # 组装为函数
    lines = []
    for line in script.splitlines():
        lines.append('   ' + line)
    code = """def complie_script(s):
%s"""   % ('\n'.join(lines))
    compile(code, '', 'exec')
