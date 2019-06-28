# conding=utf-8
"""
@project:edubalibs
@language:Python3
@create:2019/5/30
@author:qianyang<qianyang@aibayes.com>
@description:none
"""


class BayesLibsConfig:
    def __init__(self, ip, port, user_id=None, password=None):
        self.ip = ip
        self.port = port
        self.user_id = user_id
        self.password = password

    def connect(self):
        from bayeslibs.voice import ApolloChatter
        from bayeslibs.config.setting import ApolloConfig
        apollo = ApolloConfig()
        apollo.set_apollo_url(self.ip, self.port)
        apollo_speaker = ApolloChatter()
        res = apollo_speaker.start('连接成功')
        if res and res['status'] == 0:
            flag = True
            print('connect success, apollo ip:{}'.format(apollo.get_apollo_url()))
        else:
            flag = False
            print('connect failed, please reset apollo\'s ip')
        return flag


__all__ = ['BayesLibsConfig']
