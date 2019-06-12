# coding:utf-8

from tweb.license import License
import config

max_lic_text = 'cgate:11;;|employ:11;;|org:111111111;30;'


class Employment(License):
    profiles = {
        'org': {
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
        },
        'employ': {
            'switch': [
                "add",
                "remove"
            ]
        },
        'cgate': {
            'switch': [
                "open",
                "close"
            ]
        }
    }

    display = {
        'zh': {
            'org': '组织管理',
            'org.switch': '权限开关',
            'org.switch.create': '创建',
            'org.switch.read': '读取',
            'org.switch.update': '更新',
            'org.switch.remove': '删除',
            'org.switch.submit': '提交',
            'org.switch.audit': '审核',
            'org.switch.reject': '驳回',
            'org.switch.activate': '激活',
            'org.switch.deactivate': '去激活',
            'org.number': '数量限制',
            'org.number.visible_level': '可见级别',
            'employ': '人事权利',
            'employ.switch': '权限开关',
            'employ.switch.add': '添加',
            'employ.switch.remove': '移除',
            'cgate': '客户入口控制',
            'cgate.switch': '权限开关',
            'cgate.switch.open': '打开',
            'cgate.switch.close': '关闭'
        },
        'en': {
            'org': 'Organization',
            'org.switch': 'Switches',
            'org.switch.create': 'Create',
            'org.switch.read': 'Read',
            'org.switch.update': 'Update',
            'org.switch.remove': 'Remove',
            'org.switch.submit': 'Submit',
            'org.switch.audit': 'Audit',
            'org.switch.reject': 'Reject',
            'org.switch.activate': 'Activate',
            'org.switch.deactivate': 'Deactivate',
            'org.number': 'Number Limit',
            'org.number.visible_level': 'Visible Lever',
            'employ': 'Employ',
            'employ.switch': 'Switches',
            'employ.switch.add': 'Add',
            'employ.switch.remove': 'Remove',
            'cgate': 'Customer Gate Control',
            'cgate.switch': 'Switches',
            'cgate.switch.open': 'Open',
            'cgate.switch.close': 'Close'
        }
    }

    def __init__(self):
        super(Employment, self).__init__(self.profiles, self.display,
                                         authority=config.PLATFORM, secret=config.TornadoSettings['cookie_secret'])
