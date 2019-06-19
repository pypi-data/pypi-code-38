import redis
from ciperror import RedisConnectionError
import json


class RedisChecker:

    def __init__(self, logger, service_name, redis_url, redis_port):
        self.redis = redis.Redis(host=redis_url, port=redis_port, socket_timeout=5,
                 socket_connect_timeout=5)
        self.config_key = service_name + "-config"
        self.service_name = service_name
        self.logger = logger
        pass

    def check_key(self, key_name, key_time):
        try:
            int(key_time)
            if self.redis.get(name=key_name) is None:
                self.redis.set(name=key_name, value=str(True), ex=int(key_time))
                return True
            else:
                return False
        except Exception as ex:
            err = RedisConnectionError(
                "Erro de conexão com o REDIS ao tentar consultar uma key. EXCEPTION: {}".format(str(ex)))
            self.logger.error(err.code, 200, message=err.message)
            return ex

    def get_config(self):
        try:
            return self.redis.get(name=self.config_key)
        except Exception as ex:
            err = RedisConnectionError("Erro de conexão com o REDIS ao tentar pegar a configuracao do servico. EXCEPTION: {}".format(str(ex)))
            self.logger.error(err.code, 200, message=err.message)
            return ex

    def set_config(self, config):
        try:
            self.redis.set(name=self.config_key, value=json.dumps(config), ex=600)
            return True
        except Exception as ex:
            err = RedisConnectionError("Erro de conexão com o REDIS ao tentar atualizar a configuracao do servico. EXCEPTION: {}".format(str(ex)))
            self.logger.error(err.code, 200, message=err.message)
            return ex

    def healthcheck(self):
        try:
            self.redis.ping()
        except Exception as ex:
            error = RedisConnectionError("O serviço não consegue se conectar ao Redis. A aplicação não funcionará corretamente. EXCEPTION: {}".format(ex))
            return error.message
        return True
