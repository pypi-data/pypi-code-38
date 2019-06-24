#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/22
import threading

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from urllib3.util import url, Url

from api.exceptions import IllegalArgumentException
from api.model.FactDatasource import JdbcTypeEnum, JdbcDriverEnum, FactDatasourceTypeEnum
from config.annotation import Value
from factdatasource.dao.FactDatasource import DatasourceListener, MultipleBaseDatasource, BaseDatasource, \
    customer_dao_context_holder
from factdatasource.execptions import DatasourceNotFoundException, NotSupportedFDException, FDExecuteException, \
    FDConfigException
from libs import utils
from libs.utils import Singleton


class MultipleJdbcDatasource(DatasourceListener, MultipleBaseDatasource, Singleton):
    """
    管理fd中的所有JDBC类型的数据源
    """

    DEFAULT_JDBC_DATASOURCE = '_ficus4py_default_jdbc_datasource'

    def __init__(self):
        # source_name --> JdbcDatasource
        self._target_dataSources = dict()

    def get_datasource_type(self):
        """
        获取数据源类型
        :return:
        """
        return FactDatasourceTypeEnum.JDBC

    def add_datasource_type(self, source_name: str, url: str, credentials: str):
        """
        添加一个数据源
        :param source_name:
        :param url:
        :param credentials:
        :return:
        """
        if not source_name or not url:
            raise IllegalArgumentException(f'添加数据源参数错误:source_name、url都不能为空')

        for target in self._target_dataSources.values():
            if target.url == url and target.credentials == credentials:
                # url 和 credentials 都相同，说明是同一个数据库连接就不再重复创建数据源了
                target.add_source_name(source_name)
                self._target_dataSources[source_name] = target
                return

        # 开始创建数据源
        jdbc_data_source = JdbcDatasource(source_name, url, credentials)
        jdbc_data_source.start()
        self._target_dataSources[source_name] = jdbc_data_source

    def update_datasource_type(self, source_name: str, url: str, credentials: str):
        """
        修改一个数据源
        :param source_name:
        :param url:
        :param credentials:
        :return:
        """
        if not source_name or not url:
            raise IllegalArgumentException(f'修改数据源参数错误:source_name、url都不能为空')

        self.delete_datasource_type(source_name)
        self.add_datasource_type(source_name, url, credentials)

    def delete_datasource_type(self, source_name: str):
        """
        删除一个数据源
        :param source_name:
        :return:
        """
        if not source_name:
            raise IllegalArgumentException(f'删除数据源参数错误:source_name不能为空')

        target: JdbcDatasource = self._target_dataSources.pop(source_name)
        if target:
            if target.only_one_source():
                target.close_client()
            else:
                target.remove_source_name(source_name)

    def get_data_source(self):
        """
        获取数据源的基本信息
        :return:
        """
        source_name = self.determine_current_lookup_key()
        if not source_name:
            raise FDExecuteException('未设置操作源,无法获取数据源信息。')
        if source_name in self._target_dataSources.keys():
            return self._target_dataSources[source_name]
        raise DatasourceNotFoundException('未发现数据源%s,请添加后再获取。' % source_name)

    def determine_current_lookup_key(self):
        """JDBC中需要设置默认的数据源，所以这里需要重写该方法"""
        source_name = customer_dao_context_holder.get_source()
        if source_name is None:
            return self.DEFAULT_JDBC_DATASOURCE
        return source_name

    def get_client(self):
        """
        获取数据库操作的client
        :return:
        """
        target: JdbcDatasource = self.get_data_source()
        return target.get_client()

    def close_client(self):
        """
        关闭客户端，关闭连接
        :return:
        """
        target: JdbcDatasource = self.get_data_source()
        return target.close_client()


class JdbcDatasource(BaseDatasource):
    """
    JDBC数据源，存储该数据源基本信息
    """

    def __init__(self, source_name, url, credentials):
        self.init(source_name, url, credentials)
        self.__lock = threading.Lock()
        self.__client: Session = None
        self.__engine = None

    def start(self):
        """
        分析url并开始连接数据库
        :return:
        """
        sqlalchemy_url = self._parse_url()
        self.__engine = create_engine(sqlalchemy_url, case_sensitive=False, echo=True, encoding='utf-8')

    def get_client(self):
        if not self.__client:
            with self.__lock:
                if not self.__client:
                    jdbc_session = sessionmaker(bind=self.__engine, autocommit=True)
                    self.__client = jdbc_session()
        return self.__client

    def close_client(self):
        if self.__client:
            self.__client.close()

    def _parse_url(self):
        """
        分析url，并构造成能直接连接sqlalchemy的url
        :return:
        """
        if not self._url:
            return ''
        jdbc_type = utils.get_jdbc_type(self._url)
        if not jdbc_type:
            raise NotSupportedFDException(f'不支持该连接{self._url}')

        result_url = self._structure_url(jdbc_type, self.url)
        return result_url

    def _structure_url(self, jdbc_type: JdbcDriverEnum, jdbc_url: str):
        """
        由于url都是JDBC版本的url，所以需要根据不同的版本构造我们需要的url
        :param jdbc_type:
        :param jdbc_url:
        :return:  dialect[+driver]://user:password@host/dbname[?key=value..]
        """
        if not jdbc_type or not jdbc_url:
             raise IllegalArgumentException('构造url参数错误。')

        # 支持sqlalchemy进行连接的url
        if jdbc_type == JdbcTypeEnum.MYSQL:
            sqlalchemy_scheme = JdbcDriverEnum.MYSQL_DRIVER
        elif jdbc_type == JdbcTypeEnum.ORACLE:
            sqlalchemy_scheme = JdbcDriverEnum.ORACLE_DRIVER
        elif jdbc_type == JdbcTypeEnum.POSTGRESQL:
            sqlalchemy_scheme = JdbcDriverEnum.POSTGRESQL_DRIVER
        elif jdbc_type == JdbcTypeEnum.SQL_SERVER:
            sqlalchemy_scheme = JdbcDriverEnum.SQL_SERVER_DRIVER
        elif jdbc_type == JdbcTypeEnum.VERNOX:
            sqlalchemy_scheme = JdbcDriverEnum.VERNOX_DRIVER
        else:
            raise NotSupportedFDException(f'暂不支持该数据库{jdbc_type}')

        result_url = None
        if jdbc_type == JdbcTypeEnum.SQL_SERVER:
            # JDBC的通用形式是 jdbc:sqlserver://[serverName[\instanceName][:portNumber]][;property=value[;property=value]]
            url_param = {}
            if ';' in jdbc_url:
                url_list = jdbc_url.split(';', 1)
                url_prefix = url_list[0]
                url_param_tmp = url_list[1]
                # 获取配置的参数
                for param in url_param_tmp.split(';'):
                    if '=' in param:
                        p = param.split('=', 1)
                        url_param[p[0]] = p[1]
            else:
                url_prefix = jdbc_url

            r = url.parse_url(url_prefix)
            if 'databaseName' in url_param:
                database = url_param.pop('databaseName')
            else:
                raise FDConfigException(f'数据源{source_name}未配置databaseName值。')

            # 添加一个驱动参数
            if 'driver' not in url_param:
                url_param['driver'] = 'SQL Server'

            query = ''
            if url_param:
                for key, value in url_param.items():
                    query = query + str(key) + '=' + str(value) + '&'
                # 删除最后一个&
                query = query.rstrip('&')

            path = '/' + str(database)

            result_url = Url(scheme=sqlalchemy_scheme.value, auth=self._credentials, host=r.host, port=r.port, path=path, query=query, fragment=r.fragment)
        elif jdbc_type == JdbcTypeEnum.ORACLE:
            # JDBC的常用形式是
            # 1.普通SID方式
            # jdbc:oracle:thin:username/password@x.x.x.1:1521:SID
            # 2.普通ServiceName 方式
            # jdbc:oracle:thin:username/password@//x.x.x.1:1522/ABCD
            # 3.RAC方式  暂时不支持
            # jdbc:oracle:thin:@(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=x.x.x.1)(PORT=1521))(ADDRESS=(PROTOCOL=TCP)(HOST=x.x.x.2)(PORT=1521)))(LOAD_BALANCE=yes)(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=xxrac)))
            base_message = None
            if '@' in jdbc_url:
                base_message = jdbc_url.split('@', 1)[1]
            else:
                base_message = jdbc_url

            host_port = None
            service_name = None
            sid = None

            if jdbc_url.startswith('//'):
                # ServiceName 方式
                if '/' in base_message:
                    host_port = base_message.split('/', 1)[0]
                    service_name = base_message.split('/', 1)[1]
                else:
                    raise FDConfigException(f'数据源{source_name}未配置service_name值,无法解析。')
            else:
                # sid方式
                if ":" in base_message:
                    sid_message = base_message.split(':', 2)
                    if len(sid_message) == 3:
                        host_port = str(sid_message[0]) + ':' + str(sid_message[1])
                        sid = str(sid_message[2])
                    elif len(sid_message) == 2:
                        host_port = str(sid_message[0])
                        sid = str(sid_message[1])
                    else:
                        raise FDConfigException(f'数据源{source_name}无法进行有效解析。')
                else:
                    raise FDConfigException(f'数据源{source_name}无法进行有效解析。')

            if ':' in host_port:
                host = str(host_port.split(':', 1)[0])
                port = str(host_port.split(':', 1)[1])
            else:
                host = str(host_port)
                port = '1521'

            import cx_Oracle
            if service_name:
                dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
            else:
                dsn = cx_Oracle.makedsn(host, port, sid=sid)

            credentials = str(self._credentials)+'@' if self._credentials else ''
            return f'{sqlalchemy_scheme.value}://{credentials}{dsn}'
        else:
            # 默认可以使用的比较通用的构造方式
            r = url.parse_url(jdbc_url)
            # sqlalchemy mysql 这里中文一直是乱码，暂时先手动设置下编码
            query = r.query
            if jdbc_type == JdbcTypeEnum.MYSQL or jdbc_type == JdbcTypeEnum.VERNOX:
                if not query:
                    query = 'charset=utf8'
                elif str(query).lower().find('charset=') == -1:
                    query = query + '&charset=utf8'

            result_url = Url(scheme=sqlalchemy_scheme.value, auth=self._credentials, host=r.host, port=r.port, path=r.path, query=query, fragment=r.fragment)
        return result_url.url


@Value("${jdbc.ip}")
def jdbc_ip():
    pass


@Value("${jdbc.url}")
def jdbc_url():
    pass


@Value("${jdbc.username}")
def jdbc_username():
    pass


@Value("${jdbc.password}")
def jdbc_password():
    pass


def register_jdbc_default_datasource():
    """
    注册默认的数据源
    :return:
    """
    credentials = f'{jdbc_username()}:{jdbc_password()}'
    url = jdbc_url()
    datasource = MultipleJdbcDatasource.instance()
    datasource.add_datasource_type(datasource.DEFAULT_JDBC_DATASOURCE, url, credentials)
