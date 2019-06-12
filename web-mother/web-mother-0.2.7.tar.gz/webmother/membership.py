# coding:utf-8

from tweb.license import License
import config

max_lic_text = ''


# 目前关于会员在会员组织中的权利没有定义，待后续扩展。。。
class Membership(License):
    profiles = {
    }

    display = {
        'zh': {
        },
        'en': {
        }
    }

    def __init__(self):
        super(Membership, self).__init__(self.profiles, self.display,
                                         authority=config.PLATFORM, secret=config.TornadoSettings['cookie_secret'])
