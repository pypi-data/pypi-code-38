#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/22
from api.model.FactDatasource import FactDatasource
from factdatasource.execptions import NotSupportedFDException
from factdatasource.persistence.jdbc.JdbcFactDatasourceContext import JdbcFactDatasourceContext


class Db2JdbcFactDatasourceContext(JdbcFactDatasourceContext):
    """
    TODO 暂时不支持DB2
    """
    def __init__(self, fact_datasource: FactDatasource):
        raise NotSupportedFDException('暂时不支持该FD类型')
