from ..config import AiopikaDriverConfig


class AiopikaRPCDriverConfig(AiopikaDriverConfig):

    LOGO: str = """
 _____       _
|  __ \     (_)               
| |  | |_ __ ___   _____ _ __ 
| |  | | '__| \ \ / / _ \ '__|
| |__| | |  | |\ V /  __/ |   
|_____/|_|  |_| \_/ \___|_|aiopika_rpc
"""


    # Queue
    QUEUE_NAME: str = 'rpc_queue'

    # RPC
    DEFAULT_EXPIRE_CALL: int = 30
