import time

from django_websocket_server.messagetemplates import commandmessage
from django_websocket_server.websocket_server import SocketServer
from multi_purpose_arduino_controller.arduino_controller.api import ArduinoControllerAPI



class BoardControllerAPI(ArduinoControllerAPI):
    def __init__(self, **kwargs):
        kwargs.setdefault("name", "BoardControllerAPI")
        super().__init__(**kwargs)


    def port_opened(self,port):
        super().port_opened(port)
        if self.websocket_server is not None:
            self.websocket_server.send_to_all(commandmessage(cmd="port_opened",port=port,sender=self.name))

    def port_closed(self,port):
        super().port_closed(port)
        if self.websocket_server is not None:
            self.websocket_server.send_to_all(commandmessage(cmd="port_closed",port=port,sender=self.name))

    def ws_get_ports(self):
        self._python_communicator.cmd_out(cmd="get_ports",targets=["serialreader"],data_target=self.name)
        time.sleep(0.5)
        if self.websocket_server is not None:
            self.websocket_server.send_to_all(
                commandmessage(cmd="set_ports",connected_ports = list(self.connected_ports),ignored_ports = list(self.ignored_ports),available_ports=list(self.available_ports),identified_ports=list(self.identified_ports),sender=self.name)
            )

    def port_identified(self,port):
        super().port_identified(port)
        self.ws_get_ports()

    def activate_port(self,port):
        self._python_communicator.cmd_out(cmd="reactivate_port",targets=["serialreader"],port=port)

    def deactivate_port(self,port):
        self._python_communicator.cmd_out(cmd="deactivate_port",targets=["serialreader"],port=port)

    def get_board(self,port):
        self._python_communicator.cmd_out(cmd="get_board",targets=[port],data_target=self.name)

    def set_board(self,board,port):
        self.websocket_server.send_to_all(
            commandmessage(cmd="set_board",board=board,sender=self.name,port=port)
        )

    def set_board_attribute(self,port,attribute,value):
        self._python_communicator.cmd_out(cmd="set_board_attribute",targets=[port],attribute=attribute,value=value)

    def set_websocket_server(self, websocket_server:SocketServer):
        super().set_websocket_server(websocket_server)
        self.websocket_server.register_cmd("get_ports",self.ws_get_ports)
        self.websocket_server.register_cmd("activate_port",self.activate_port)
        self.websocket_server.register_cmd("deactivate_port",self.deactivate_port)
        self.websocket_server.register_cmd("get_board",self.get_board)
        self.websocket_server.register_cmd("set_board_attribute",self.set_board_attribute)

