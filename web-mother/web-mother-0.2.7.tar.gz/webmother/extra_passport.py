import config
from .passport import Passport
from tweb.license import License
from webmother.service import ctrl_passport

system_name = 'tree'

max_lic_text = 'catalog:111111111;30;'
profiles = {
    'catalog': {
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
        ]
    }
}
display = {
    'zh': {
        'catalog': '分类操作',
        'catalog.switch': '权限开关',
        'catalog.switch.create': '创建',
        'catalog.switch.read': '读取',
        'catalog.switch.update': '更新',
        'catalog.switch.remove': '删除',
        'catalog.switch.submit': '提交',
        'catalog.switch.audit': '审核',
        'catalog.switch.reject': '驳回',
        'catalog.switch.activate': '激活',
        'catalog.switch.deactivate': '去激活',
        'catalog.number': '数量限制',
        'catalog.number.visible_level': '可见级别'
    },
    'en': {
        'catalog': 'Catalog',
        'catalog.switch': 'Switches',
        'catalog.switch.create': 'Create',
        'catalog.switch.read': 'Read',
        'catalog.switch.update': 'Update',
        'catalog.switch.remove': 'Remove',
        'catalog.switch.submit': 'Submit',
        'catalog.switch.audit': 'Audit',
        'catalog.switch.reject': 'Reject',
        'catalog.switch.activate': 'Activate',
        'catalog.switch.deactivate': 'Deactivate',
        'catalog.number': 'Number Limit',
        'catalog.number.visible_level': 'Visible Lever'
    }
}


def append_extra():
    # 添加本系统涉及到的权限项
    Passport.add_system_profile(system_name, profiles, display)

    # 更新超级管理员的账户相关权限
    extra_lic = License(profiles, display).parse(max_lic_text)
    ctrl_passport.simple_update('0', '0', extra_lic.json)
