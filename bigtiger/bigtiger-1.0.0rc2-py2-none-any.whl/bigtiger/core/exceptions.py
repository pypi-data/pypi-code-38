# -*- coding: utf-8 -*-


class BigTigerError(Exception):

    @property
    def message(self):
        return self.args[0]


class DBError(BigTigerError):
    """数据库操作失败。"""
    pass


class DBRefError(DBError):
    """数据关联错误。"""

    @property
    def message(self):
        ref = self.args[0]
        return '关联数据"%(ref_desc)s", %(ref_count)d条' % {'ref_desc': ref.ref_desc, 'ref_count': ref.ref_count}


class SuspiciousOperation(BigTigerError):
    """可疑操作异常，常用于客户端用户提醒"""
    pass


class ImportDataError(Exception):
    """导入数据错误"""

    @property
    def message(self):
        return self.args[0]

    @property
    def excel_errors(self):
        return self.args[1]


class PermissionError(Exception):
    """权限异常"""
    pass


class AuthenticateError(Exception):
    """用户认证错误"""
    pass
