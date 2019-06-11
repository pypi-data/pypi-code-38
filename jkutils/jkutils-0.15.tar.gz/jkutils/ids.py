import threading
from datetime import datetime

lock = threading.Lock()

_auto_id = 0


def serial_number(service_number, zk_node_number, business_number):
    """
    生成业务流水号

    1、4字节服务号

        每一个服务都有服务编号，采用各自的服务编号即可，参考 服务规范 。

    2、7字节服务节点编号

        每一类会有若干节点，这里是每一个节点的编号。此处采用zk临时节点名字的后7位。比如节点名为server0000023551，则取值为0023551。

    3、5字节业务识别号

        业务识别号，比如注册为10002，每个服务内部自己编排业务识别码。不关心业务号的，也可全部为00000。

    4、16字节序列号

        为64位整数，只取低53位，转换为字符串。

        在这53位中，高42位取当前unix时间戳(毫秒)，低11位为程序内部维护自增id(溢出归0)。

        例如：ms表示当前毫秒时间，id为自增id，则序列号为 ((ms & 0x3FFFFFFFFFF) << 11) | (tran_id & 0x7ff)。
    """
    try:
        lock.acquire()
        global _auto_id
        _auto_id += 1
        return "".join(
            [
                service_number,
                zk_node_number,
                business_number,
                str(((int(datetime.now().timestamp() * 1000) & 0x3FFFFFFFFFF) << 11) | (_auto_id & 0x7FF)),
            ]
        )
    except Exception as e:
        print(e)
    finally:
        lock.release()
