from webmother.passport import Passport
from tweb.license import License
from webmother.service import ctrl_passport

system_name = 'wallet'

max_lic_text = 'contract:11111;;'
profiles = {
    'contract': {
        'switch': [
            "create",
            "read",
            "remove",
            "activate",
            "deactivate"
        ]
    }
}
display = {
    'zh': {
        'contract': '合约管理',
        'contract.switch': '权限开关',
        'contract.switch.create': '创建',
        'contract.switch.read': '读取',
        'contract.switch.remove': '移除',
        'contract.switch.activate': '激活',
        'contract.switch.deactivate': '冻结',
    },
    'en': {
        'contract': 'Contract Manage',
        'contract.switch': 'Switches',
        'contract.switch.create': 'Create',
        'contract.switch.read': 'Read',
        'contract.switch.remove': 'Remove',
        'contract.switch.activate': 'Activate',
        'contract.switch.deactivate': 'Deactivate',
    }
}


def append_extra():
    # 添加本系统涉及到的权限项
    Passport.add_system_profile(system_name, profiles, display)

    # 更新超级管理员的账户相关权限
    extra_lic = License(profiles, display).parse(max_lic_text)
    ctrl_passport.simple_update('0', '0', extra_lic.json)
