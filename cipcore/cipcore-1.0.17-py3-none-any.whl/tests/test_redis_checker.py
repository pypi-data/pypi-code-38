import fakeredis
from mock import MagicMock
from cipcore import RedisChecker

logger = MagicMock()
service_name = "teste"
redis_url = "http://localhost"
redis_port = 1234
key_name = "foo"
key_time = int(1000)
redis_error = 'FakeRedis is emulating a connection error.'

def test_constructor():
    redisObj = RedisChecker(logger, service_name, redis_url, redis_port)

    assert(redisObj.service_name == service_name)
    assert(redisObj.config_key == service_name + "-config")
    assert(redisObj.logger == logger)

def test_check_key():
    redisObj = RedisChecker(logger, service_name, redis_url, redis_port)
    redisObj.redis = fakeredis.FakeStrictRedis()
    checkKey = redisObj.check_key(key_name, key_time)
    checkKey2 = redisObj.check_key(key_name, key_time)

    assert (checkKey == True)
    assert (checkKey2 == False)

def test_get_config():
    redisObj = RedisChecker(logger, service_name, redis_url, redis_port)
    redisObj.redis = fakeredis.FakeStrictRedis()
    redisObj.redis.set("teste-config", "bar")
    checkGetConfig = redisObj.get_config()

    assert (checkGetConfig == b'bar')

def test_set_config():
    redisObj = RedisChecker(logger, service_name, redis_url, redis_port)
    redisObj.redis = fakeredis.FakeStrictRedis()
    redisObj.set_config('{"foo": "bar"}')
    checkGetConfig = redisObj.get_config()

    assert (checkGetConfig == b'"{\\"foo\\": \\"bar\\"}"')

def test_healthcheck():
    redisObj = RedisChecker(logger, service_name, redis_url, redis_port)
    redisObj.redis = fakeredis.FakeStrictRedis()
    checkHealthcheck = redisObj.healthcheck()

    assert (checkHealthcheck == True)

def test_check_key_redis_error():
    server = fakeredis.FakeServer()
    server.connected = False
    redisObj = RedisChecker(logger, service_name, redis_url, redis_port)
    redisObj.redis = fakeredis.FakeStrictRedis(server=server)
    checkKeyError = redisObj.check_key(key_name, key_time)

    assert(checkKeyError.args[0] == redis_error)

def test_get_config_error():
    server = fakeredis.FakeServer()
    server.connected = True
    redisObj = RedisChecker(logger, service_name, redis_url, redis_port)
    redisObj.redis = fakeredis.FakeStrictRedis(server=server)
    redisObj.redis.set("teste-config", "bar")
    server.connected = False
    checkGetConfig = redisObj.get_config()

    assert(checkGetConfig.args[0] == redis_error)

def test_healthcheck_error():
    server = fakeredis.FakeServer()
    server.connected = True
    redisObj = RedisChecker(logger, service_name, redis_url, redis_port)
    redisObj.redis = fakeredis.FakeStrictRedis(server=server)
    server.connected = False
    checkHealthCheckError = redisObj.healthcheck()

    assert(checkHealthCheckError == 'Erro de conexão com o Redis: MESSAGE: O serviço não consegue se conectar ao Redis. A aplicação não funcionará corretamente. EXCEPTION: FakeRedis is emulating a connection error.')