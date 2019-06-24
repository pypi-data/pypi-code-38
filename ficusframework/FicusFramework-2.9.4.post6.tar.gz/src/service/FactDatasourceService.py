#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/30
from api.model.FactDatasource import FactDatasource
from factdatasource.dao.jdbc.JdbcDatasourceDao import JdbcDatasourceDao
from libs.utils import Singleton


class FactDatasourceService(Singleton):

    @property
    def dao(self):
        return JdbcDatasourceDao.instance()

    def get_fd_by_code(self, fd_code: str) -> FactDatasource:
        """
        根据code查询FD的信息
        :param fd_code: 数据源code,code具有全局唯一性，所以这里可以直接根据code查询出数据
        :return: FactDatasource
        """
        if not fd_code:
            return None

        sql = f"""SELECT id,site,projectCode,code,name,description,type,connection,credentials,target,modelid AS model,ttl,tags,privilege
            FROM `sc_factdatasource` WHERE CODE=:fd_code"""
        code_dict = {'fd_code': fd_code}
        fd = self.dao.select_one(sql, code_dict)
        if fd:
            return FactDatasource(**fd)
        return None

    def exists_fds(self, fd_codes: list) -> bool:
        """
        判断fd_codes是否全部存在
        :param fd_codes:
        :return: bool
        """
        if not fd_codes:
            return False

        sql = f'SELECT code FROM `sc_factdatasource` WHERE code IN :fd_codes'
        codes_dict = {'fd_codes': fd_codes}
        codes_result = self.dao.select_all(sql, codes_dict)
        if codes_result:
            codes_list = [re['code'] for re in codes_result]
            if len(fd_codes) == len(codes_list):
                return True
        return False

