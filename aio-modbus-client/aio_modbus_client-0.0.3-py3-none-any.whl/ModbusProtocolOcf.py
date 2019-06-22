from .ModbusProtocol import ModbusProtocol
import base64


class ModbusProtocolOcf(ModbusProtocol):

    async def execute(self, message, serial):
        data = await self.transport.request(
            'update',
            self.transport.link_master,
            dict(
                slave=message.slave_id,
                function=message.function_code,
                pdu=base64.b64encode(message.encode()).decode(),
                answerSize=message.get_response_pdu_size(),
                **serial
            )
        )
        data = base64.b64decode(data.cn.encode())
        response = message.response()
        response.decode(data)
        return response


class OcfMessageRequest:
    def __init__(self, **kwargs):
        self.slave_id = kwargs['slave']
        self.function_code = kwargs['function']
        self.pdu = self.b64encode(kwargs['pdu'])
        self.response_pdu_size = kwargs['answerSize']
        self.response = OcfMessageResponse

    def encode(self):
        return self.pdu

    def get_response_pdu_size(self):
        return self.response_pdu_size

    @staticmethod
    def b64decode(data):
        # convert string base64 data to byte
        return base64.b64encode(data).decode()

    @staticmethod
    def b64encode(data):
        # convert byte to base64 string
        return base64.b64decode(data.encode())


class OcfMessageResponse:
    def __init__(self):
        self.pdu = None

    def decode(self, pdu):
        self.pdu = pdu

    def b64decode(self):
        # convert string base64 data to byte
        return base64.b64encode(self.pdu).decode()
