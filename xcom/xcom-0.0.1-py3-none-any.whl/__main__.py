import sys
import asyncio
import argparse
import logging

from .modbus.modbus_server import MbProtocol
from .tools import bytes_to_str
from .log_config import configure_arg_parser, configure_logger


def _configure_args(parser):
    parser.add_argument('-i', '--iface', help='Listen interface', default='localhost')
    parser.add_argument('--port', help='Listen TCP port', default=0, type=int)
    parser.add_argument('-p', '--protocol', help='Protocol')
    parser.add_argument('devices', nargs=argparse.REMAINDER)


class ProtocolWrapper(asyncio.Protocol):
    Log = None
    ProtocolClass = None
    
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        self.Log.info('Connection from {}'.format(peername))
        self.transport = transport                              # pylint: disable=attribute-defined-outside-init
        self.p = ProtocolWrapper.ProtocolClass()                # pylint: disable=attribute-defined-outside-init, not-callable

    def data_received(self, data):
        self.Log.debug(f'R< [{len(data)}b] ' + bytes_to_str(data))

        resp = self.p.get_response(data)
        if resp:
            self.Log.debug(f'S> [{len(resp)}b] ' + bytes_to_str(resp))
            self.transport.write(resp)

    def connection_lost(self, exc):
        self.Log.warn(f'Close the client socket: {exc}')
        self.transport.close()


def main():
    
    log = None
    
    try:
        # Args
        arg_parser = argparse.ArgumentParser()
        _configure_args(arg_parser)
        configure_arg_parser(arg_parser)
        env = arg_parser.parse_args()

        # Logging
        configure_logger(env)
        log = logging.getLogger()

        if not env.protocol:
            raise UserWarning('Protocol is not specified')

        if env.protocol != 'modbus':
            raise UserWarning(f'Unknown protocol: "{env.protocol}". Use "modbus"')

        ProtocolWrapper.Log = log
        ProtocolWrapper.ProtocolClass = MbProtocol
        ProtocolWrapper.ProtocolClass.parse_config(env.devices, log)

        loop = asyncio.get_event_loop()
        port = env.port or ProtocolWrapper.ProtocolClass.DefaultPort
        log.info('Start %s on %s:%s', ProtocolWrapper.ProtocolClass, env.iface, port)
        coro = loop.create_server(ProtocolWrapper, env.iface, port)
        server = loop.run_until_complete(coro)    
        
        try:
            log.info('Started communications')
            loop.run_forever()
        except KeyboardInterrupt:
            pass

        log.info("Closing server")
        
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()

        return 0
        
    except UserWarning as ex:
        if log:
            log.fatal(ex)
        else:
            print(ex)
        
    finally:
        logging.shutdown()


if __name__ == "__main__":
    sys.exit(main())
    