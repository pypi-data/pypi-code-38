from jkutils.env import EnvZk
from jkutils.ids import serial_number


def test_sn():
    ez = EnvZk("127.0.0.1:2181", "chaos", "localhost:12345")
    sn = serial_number("1020", ez.zk_node_number, "00001")
    print("=====sn=======", sn)  # 10200000012000013178922453168129
    assert sn is not None
