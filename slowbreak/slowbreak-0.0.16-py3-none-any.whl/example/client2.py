from slowbreak import comm
from slowbreak.session import InitiatorSessionApp
import logging
import sys
from slowbreak.app import ByMessageTypeApp, on, stack
from slowbreak.constants import MsgType
from slowbreak.message import Message, from_int
import datetime

class MyApp(ByMessageTypeApp):
    
    @on(MsgType.Logon)
    def on_logon(self, message):
        account = b"ACCOUNT"
        client_order_id = b"client_order_id"
        type_ = 2 # LIMIT
        price = 12.50
        size = 1000
        side = 1 # BUY
        symbol = b"ASYMBOL"
        
        self.send(Message(
            (35, MsgType.NewOrderSingle),
            (1,  account ),
            (11, client_order_id),
            (38, from_int(size) ),
            (40, from_int(type_) ), 
            (44, b"%.2f" % price),
            (54, from_int(side) ),
            (60, datetime.datetime.utcnow().strftime('%Y%m%d-%H:%M:%S').encode('ascii')),
            (55, symbol)
        ))

        return message

def main(argv):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    fingerprint = "" if len(argv) < 2 else argv[1]
    sock = comm.ssl_connect("127.0.0.1", 34567, [fingerprint])
    
    s = stack(
        ( InitiatorSessionApp,
            dict(
                socket = sock,
                username = b"user",
                password = b"password",
                we = b"client1",
                you = b"server1",
                reset_seq_nums=True,
                test_mode=True,
                reconnect=False,
            )
        ), 
        ( MyApp, dict())
    )
    input("ENTER TO EXIT")
    s.logout()

if __name__ == '__main__':
    sys.exit( main(sys.argv) )