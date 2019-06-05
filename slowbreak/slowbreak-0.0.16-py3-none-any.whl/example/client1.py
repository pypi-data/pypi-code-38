from slowbreak import comm
from slowbreak.session import InitiatorSessionApp

def connect(fingerprint=""):
    
    sock = comm.ssl_connect("127.0.0.1", 34567, [fingerprint])
    return InitiatorSessionApp(
        socket = sock,
        username = b"user",
        password = b"password",
        we = b"client1",
        you = b"server1",
        reset_seq_nums=True,
        test_mode=True,
        reconnect=False,
    )
    