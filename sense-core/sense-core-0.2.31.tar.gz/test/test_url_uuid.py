import sense_core as sd
from sense_core import url_uuid

sd.log_init_config('core', '/tmp/', 'rabbit_monit')


def test_get_url_uuid():
    uuid = url_uuid.get_url_uuid("http://52.82.48.248:4006/stock/detail/300216")
    print(uuid)


def test_get_url_uuid_list():
    uuid = url_uuid.get_url_uuid_list("http://52.82.48.248:4006/stock/detail/300216")
    print(uuid)
