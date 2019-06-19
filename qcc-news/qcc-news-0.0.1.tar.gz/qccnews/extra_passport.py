from webmother.passport import Passport
from tweb.license import License
from webmother.service import ctrl_passport

system_name = 'news'

max_lic_text = 'news:111111111;30;'
profiles = {
    'news': {
        'switch': [
            "create",
            "read",
            "update",
            "remove",
            "submit",
            "audit",
            "reject",
            "activate",
            "deactivate"
        ],
        'number': [
            "visible_level"  # 资源可见级别，越大表示可以看到status值更低的资源，取值范围为资源status取值范围，如0～40
        ],
    }
}
display = {
    'zh': {
        'news': '新闻管理',
        'news.switch': '权限开关',
        'news.switch.create': '创建',
        'news.switch.read': '读取',
        'news.switch.update': '更新',
        'news.switch.remove': '移除',
        'news.switch.submit': '提交',
        'news.switch.audit': '审核',
        'news.switch.reject': '驳回',
        'news.switch.activate': '上架',
        'news.switch.deactivate': '下架',
        'news.number': '数量限制',
        'news.number.visible_level': '可见级别',
    },
    'en': {
        'news': 'News Manage',
        'news.switch': 'Switches',
        'news.switch.create': 'Create',
        'news.switch.read': 'Read',
        'news.switch.update': 'Update',
        'news.switch.remove': 'Remove',
        'news.switch.submit': 'Submit',
        'news.switch.audit': 'Audit',
        'news.switch.reject': 'Reject',
        'news.switch.activate': 'Activate',
        'news.switch.deactivate': 'Deactivate',
        'news.number': 'Number Limit',
        'news.number.visible_level': 'Visible Level',
    }
}


def append_extra():
    # 添加本系统涉及到的权限项
    Passport.add_system_profile(system_name, profiles, display)

    # 更新超级管理员的账户相关权限
    extra_lic = License(profiles, display).parse(max_lic_text)
    ctrl_passport.simple_update('0', '0', extra_lic.json)
