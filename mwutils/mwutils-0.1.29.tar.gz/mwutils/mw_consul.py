'''
window下的測試
consul agent -server -bootstrap-expect 1 -data-dir data-dir -bind=127.0.0.1 -ui-dir ./consul_ui/ -rejoin -config-dir=consul.d -client 0.0.0.0
curl http://127.0.0.1:8500/v1/catalog/services
'''
from consul import Consul

def reg_service(name,address =None,port=None,tags=None,check=None,token=None,consul=None):
    '''
    向consul 中注册服务
    :param name:服務名稱
    :param address: 服務ip
    :param port: 服務 port
    :param tags:
    :param check:
    :param token:
    :return:
    '''
    if consul is None:
        cons = Consul()
    else:
        cons = consul
    try:
        agent_self = cons.agent.self()
    except Exception as e:
        print('访问consul失败,error:%s' % ( e))
        import sys
        sys.exit(-1)
    member = agent_self['Member']
    node_name = member.get('Name')
    if not address:
        address = member.get('Addr')
    try:
        cons.agent.service.register(name,service_id='%s:%s:%s'%(node_name,name,port or ''),address=address,port=port,tags=tags,check=check,token=token)
        print('註冊%s到consul成功！'%name)
    except Exception as e:
        print('注册 %s服务失败,error:%s' % (name, e))
        import sys
        sys.exit(-1)

def dereg_service(servicer_name, web_port, node_name=None, consul=None, service_id=None):
    '''
    consul中的服务注销服务
    :param servicer_name: 服务名称
    :param web_port:
    :return:
    '''
    if consul is None:
        cons = Consul()
    else:
        cons = consul
    try:
        if service_id:
            cons.agent.service.deregister(service_id)
        else:
            agent_self = cons.agent.self()
            member = agent_self['Member']
            if node_name is None:
                node_name = member.get('Name')
            service_id='%s:%s:%s'%(node_name, servicer_name, web_port or '')
            cons.agent.service.deregister(service_id)
        print('删除(%s)成功！' % servicer_name)
    except Exception as e:
        print('删除 %s服务失败,error:%s' % (servicer_name, e))
        import sys
        sys.exit(-1)

class AgentConf():
    '''
    獲取本機agent 的nodename，ip和consul 集群內的service
    '''
    def __init__(self):
        self.consul = Consul()
        try:
            agent_self = self.consul.agent.self()
            member = agent_self['Member']
            self._node_name = member.get('Name')
            self._bind_ip = member.get('Addr')
            self._services = self.consul.catalog.services()[1]
        except Exception as e:
            print('读取consul 服务失败,error:%s' % (e))
            import sys
            sys.exit(-1)

    @property
    def node_name(self):
        return self._node_name

    @property
    def bind_ip(self):
        '''
        agent 綁定的IP
        :return:
        '''
        return self._bind_ip

    @property
    def services(self):
        return self._services

    def __repr__(self):
        return 'node_name:%s,bind_ip:%s,services:%s'%(self.node_name,self.bind_ip,self.services)

    def reg_service(self,name, address=None, port=None, tags=None, check=None, token=None, consul=None):
        '''
        向consul 中注册服务
        :param name:
        :param address:
        :param port:
        :param tags:
        :param check:
        :param token:
        :param consul:
        :return:
        '''
        reg_service(name,address,port,tags,check,token,self.consul)

    def dereg_service(self,name, web_port,service_id=None):
        '''
        删除节点上的服务
        :param name:
        :param web_port:
        :param node_name:
        :return:
        '''
        dereg_service(name,web_port,self.node_name,self.consul,service_id=service_id)

class ServiceConf():
    '''
    读取通用服务配置
    '''

    def get_keyvalue(self, key, default=None):
        '''
        获取kvstore的value
        :param key: kvstore中的key
        :param default: 如果kv 不存在则返回default
        :return:
        '''
        kv = self.consul.kv.get(key)[1]
        if not kv:
            print('warring:The consul.kv(%s) of %s is not exist!' % (key, self.service_name))
            return default
        return kv['Value'].decode()

    def __init__(self, service_name, tag=None,near=False,no_exist_exit=True):
        '''
        获取服务的信息
        :param service_name: 服务名称
        :param keys: key-value存储键中的keys
        :param no_exist_exit: 如果服务不存在，直接退出系统
        :param tag: 服务的tags
        '''
        self.service_name = service_name
        self.consul = Consul()
        try:
            rl_srv = self.consul.catalog.service(service_name, tag=tag,near = self.consul.agent.self()['Config']['NodeName'] if near else None)[1]
            if not rl_srv:
                raise Exception('The %s config is not exist!' % service_name)
        except Exception as e:
            print('warring:读取%s.%s config失败，error:%s' % (service_name,tag, e))
            if no_exist_exit:
                import sys
                sys.exit(-1)
            else:
                self._address = None
                self._port = None
                self._agent_ip = None
                self._tags = []
                self._services = []
                return
        self._address = rl_srv[0]['ServiceAddress']
        self._port = rl_srv[0]['ServicePort']
        self._agent_ip = rl_srv[0]['Address']
        self._tags = rl_srv[0]['ServiceTags']
        self._services = []
        for rs in rl_srv:
            self._services.append({k: v for k, v in rs.items() if k in {'ServiceAddress', 'ServicePort', 'ServiceTags'}})

    @property
    def ip(self):
        '''
        服务的ip 同address
        :return:
        '''
        return self._address

    @property
    def address(self):
        '''
        服务的地址，同IP
        :return:
        '''
        return self._address

    @property
    def port(self):
        '''
        服务的port
        :return:
        '''
        return self._port

    @property
    def agent_ip(self):
        '''
        本機的ip地址
        :return:
        '''
        return self._agent_ip

    @property
    def tags(self):
        '''
        服务的tags，包含服务的所有tag
        :return:
        '''
        return self._tags

    @property
    def services(self):
        '''
        同一服务的多个服务配置
        :return:
        '''
        return self._services

    def __repr__(self):
        return 'ip:%s,port:%s,agent_ip:%s,tags:%s,services:%s' % (
            self._address, self._port, self._agent_ip, self.tags, self.services)


class RedisConf():
    '''
    取master 模式的redis的配置，用於寫
    '''
    def __init__(self,tag,near=False,no_exist_except=True):
        '''
        获取redis的配置
        :param tag:
        :param db: redis的db
        :param no_exist_except: 服务配置不存在时弹例外，并退出
        :param near: 取離該節點最近的redis，通常可在本機會部署一個redis
        '''
        sc = ServiceConf('redis',tag=tag,near=near,no_exist_exit=no_exist_except)
        self._ip = sc.address
        self._port = sc.port
        self._db = sc.get_keyvalue('redis_%s_db' % tag, 0)

    @property
    def ip(self):
        return self._ip
    @property
    def port(self):
        return self._port
    @property
    def db(self):
        return self._db
    def redis_url(self):
        return 'redis://%s:%s/%s' % (self.ip,self.port,self.db)

    def __repr__(self):
        return 'redis:%s'%self.redis_url()

class RedisConfMaster(RedisConf):
    '''
    取master 模式的redis的配置，用於寫
    '''
    def __init__(self):
        '''
        读取redis master的配置
        '''
        super(RedisConfMaster,self).__init__(tag='master',near=False)

class RedisConfSlave(RedisConf):
    '''
    離本節點最近的slave redis 的配置，用於讀,沒有讀到slave時，通過設定可使用master配置
    '''
    def __init__(self,onlySlave=True):
        '''
        離本節點最近的slave redis 的配置，用於讀,沒有讀到slave時，通過設定使用master配置
        :param onlySlave: True只使用slave，False slave不存在時取master 配置
        '''
        super(RedisConfSlave, self).__init__(tag='slave', near=True,no_exist_except=onlySlave)
        # 如果沒有取到slave 就取master
        if not self._ip and not onlySlave:
            rds_conf_master = RedisConfMaster()
            self._ip = rds_conf_master.ip
            self._port = rds_conf_master.port
            self._db = rds_conf_master.db

    @property
    def ip(self):
        return self._ip
    @property
    def port(self):
        return self._port
    @property
    def db(self):
        return self._db
    def redis_url(self):
        return 'redis://%s:%s/%s' % (self.ip,self.port,self.db)

    def __repr__(self):
        return 'redis slave:%s'%self.redis_url()

class DatabaseConf():
    def __init__(self,dbname='maxbus'):
        '''
        获取名称为maxbus的database服务的配置
        :param dbname:
        :param dbdriver:
        '''
        sc = ServiceConf('database', tag=dbname)
        self._host = sc.address
        self._port = sc.port
        self._dbdriver = 'mssql+pymssql' if sc.get_keyvalue('%s_dbdriver' % dbname) == 'mssql' else 'mysql+mysqldb'
        self._name = sc.get_keyvalue('%s_db_name' % dbname)
        self._user = sc.get_keyvalue('%s_login_user' % dbname)
        self._password = sc.get_keyvalue('%s_login_pw' % dbname)

    @property
    def name(self):
        return self._name
    @property
    def host(self):
        return self._host
    @property
    def port(self):
        return self._port
    @property
    def user(self):
        return self._user
    @property
    def password(self):
        return self._password
    def sqlalchemy_database_uri(self):
        return "{dbdriver}://{us}:{pw}@{host}:{port}/{name}".format(
                 dbdriver =self._dbdriver,us=self._user,pw=self._password,
                 host=self._host,port=self._port,name=self._name)

    def is_null(self):
        '''
        如果是mysql则返回 ifnull，否则返回isnull
        :return: 如果是mysql则返回 ifnull，否则返回isnull
        '''
        return 'ifnull' if self.sqlalchemy_database_uri().startswith('mysql+mysqldb') else 'isnull'

    def __repr__(self):
        return 'db config:%s'% self.sqlalchemy_database_uri()

class KongConf():
    '''
    取kong的配置
    '''
    def __init__(self):
        '''
        取kong的配置
        '''
        sc = ServiceConf('kong', tag='kong')
        self._ip = sc.address
        self._port = sc.port
        self._agent_ip = sc.agent_ip

    @property
    def ip(self):
        # kong的ip
        return self._ip

    @property
    def port(self):
        return self._port

    @property
    def agent_ip(self):
        # 本機的ip地址
        return self._agent_ip

    def host_url(self):
        return 'http://%s:%s' % (self.ip, self.port)

    def __repr__(self):
        return 'kong: %s'%self.host_url()

class KongAdminConf():
    '''
    取kong Admin的配置
    '''
    def __init__(self):
        '''
        取kong Admin的配置
        '''
        sc = ServiceConf('kong', tag='admin')
        self._ip = sc.address
        self._port = sc.port
        self._agent_ip =sc.agent_ip

    @property
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    @property
    def agent_ip(self):
        # 取得本機IP
        return self._agent_ip

    def host_url(self):
        return 'http://%s:%s' % (self.ip, self.port)

    def __repr__(self):
        return 'kong admin:%s'%self.host_url()

class KafkaConf():
    '''
    取kafka的配置
    '''
    def __init__(self):
        '''
        取kafka的配置
        '''
        self._bootstrap_servers = []
        for kfk in ServiceConf('kafka').services:
            self._bootstrap_servers.append('%s:%s'%(kfk['ServiceAddress'],
                                                   kfk['ServicePort']))
    @property
    def bootstrap_servers(self):
        return ','.join(self._bootstrap_servers)

    def __repr__(self):
        return 'bootstrap_servers:%s'%self.bootstrap_servers

class Cassandra():
    '''
    取Cassandra的配置
    '''
    def __init__(self):
        '''
        取Cassandra的配置
        '''
        self._cluster = []
        for cassd in ServiceConf('cassandra').services:
            self._cluster.append(cassd['ServiceAddress'])
    @property
    def cluster(self):
        return self._cluster

    def __repr__(self):
        return 'cluster:%s'%self._cluster


if __name__ == '__main__':
    rcw = RedisConfMaster()
    print('rcw',rcw.redis_url())
    rcr = RedisConfSlave(True)
    print('rcr',rcr.redis_url())
    db = DatabaseConf()
    print(db.sqlalchemy_database_uri())
    k = KongConf()
    print(k.host_url())
    kadm = KongAdminConf()
    print(kadm.host_url())
    kfk = KafkaConf()
    print(kfk.bootstrap_servers)
    ag = AgentConf()
    print(ag.bind_ip,ag.node_name,ag.services)
    sc = ServiceConf('realtime-server')
    print(sc)
    print(sc.get_keyvalue('maxbus_db_name'))
    print(sc.get_keyvalue('maxbus_login_user'))
    print(sc.get_keyvalue('ttttt', 'aaaaa'))


