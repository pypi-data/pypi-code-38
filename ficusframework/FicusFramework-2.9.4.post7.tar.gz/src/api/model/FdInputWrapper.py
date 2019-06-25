from api.exceptions import IllegalArgumentException
from factdatasource import FactDatasourceProxyService


class FdInputWrapper:
    """
    fd输入的一个包装
    """
    __fd_code = None
    __join_fd_codes = set()

    def fd_code(self):
        return self.__fd_code

    def __init__(self, fd_code):
        self.__fd_code = fd_code
        self.__join_fd_codes.add(fd_code)

    def join(self, other_fd_input):
        """
        合并两个fd的查询
        :param other_fd_input:
        :return:
        """
        # 1.check 两个fd的 链接是不是同一个,只能是同一个的才能链接
        this_fact_datasource = FactDatasourceProxyService.fd_client_proxy().fd(self.__fd_code)
        other_fact_datasource = FactDatasourceProxyService.fd_client_proxy().fd(other_fd_input.fd_code())

        if this_fact_datasource is None or other_fact_datasource is None:
            raise IllegalArgumentException(f"无法联合两个FD({self.__fd_code},{other_fd_input.fd_code()}),无法查询到FD数据")

        if this_fact_datasource.type != other_fact_datasource.type:
            raise IllegalArgumentException(f"无法联合两个FD({self.__fd_code},{other_fd_input.fd_code()}),两个FD的类型不相同")

        if this_fact_datasource.connection != other_fact_datasource.connection:
            raise IllegalArgumentException(f"无法联合两个FD({self.__fd_code},{other_fd_input.fd_code()}),两个FD的连接不相同")

        self.__join_fd_codes.add(other_fd_input.fd_code())
        return self

    def query(self, query, parameters={}):
        """
        对fd进行查询
        :param query: 查询语句
        :param parameters: 上下文参数
        :return: Munch对象数据
        """
        # TODO 这个地方需要对query进行校验.验证他涉及的表是不是都是fd里面的

        if self.__fd_code not in self.__join_fd_codes:
            raise IllegalArgumentException(f"来源FD不存在:{self.fd_code()}")

        return FactDatasourceProxyService.fd_client_proxy().query(self.__fd_code, query, parameters)

    def info(self):
        """
        获取fd的信息
        :return:
        """
        return FactDatasourceProxyService.fd_client_proxy().fd(self.__fd_code)
