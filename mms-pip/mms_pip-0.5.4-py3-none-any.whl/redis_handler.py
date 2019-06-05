import redis


class Redis(object):
    '''
    Class to handle easy with redis...
    '''

    def create_redis_client(self, host, port, password):
        '''
        Function to create redis client
        '''
        redis_client = redis.Redis(host=host, port=port, password=password)
        return redis_client

    def __init__(self, host, port, password, exp=60*15):
        self.host = host
        self.port = port
        self.password = password
        self.exp = exp
        self.redis_client = self.create_redis_client(self.host, self.port, self.password)

    def set_redis(self, set_key, set_value):
        '''
        :param set_key: specify the key you want to set
        :param set_value: value you want to set
        :return: None
        '''
        self.redis_client.set(set_key, set_value, ex=self.exp)

    def get_redis(self, get_key):
        return self.redis_client.get(get_key)

    def delete_key(self, key):
        self.redis_client.delete(key)

