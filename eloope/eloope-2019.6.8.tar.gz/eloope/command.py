from . import service_pb2_grpc, service_pb2
import grpc


class Command:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    @classmethod
    def execute(cls, cmd, host='localhost', port=6991):
        if cmd in ['help', 'stop', 'start', 'save', 'quit', 'task_total', 'task_count', 'start_time', 'connect']:
            return getattr(cls(host, port), cmd)()
        else:
            return 'Command error. please input "help" to view the commands help'

    def _send_command(self, cmd):
        try:
            channel = grpc.insecure_channel(f'{self.host}:{self.port}')
            stub = service_pb2_grpc.ControllerStub(channel)
            resp = stub.SendCommand(service_pb2.SendCommandRequest(command=cmd))
            return resp.info
        except grpc.RpcError:
            raise ConnectionError(f'Not connected to the server({self.host}:{self.port}).')

    @staticmethod
    def help():
        return """Commands list:
            help --- view the list of commands.
            stop --- stop sending tasks to the client.
            start --- start sending tasks to the client.
            save --- save the task to a file.
            quit --- quit the server and clients.
            task_total --- total number of tasks.
            task_count --- number of tasks on the server.
            start_time --- start time.
            connect --- connect to the server.
        """

    def stop(self):
        return self._send_command('stop')

    def start(self):
        return self._send_command('start')

    def save(self):
        return self._send_command('save')

    def quit(self):
        return self._send_command('quit')

    def task_total(self):
        return self._send_command('task_total')

    def task_count(self):
        return self._send_command('task_count')

    def start_time(self):
        return self._send_command('start_time')

    def connect(self):
        self._send_command('connect')
        print(f'Successfully connected to the server({self.host}:{self.port}).')
        print('Note: input "exit" to exit.')

        while True:
            cmd = input('Command: ')
            if cmd == 'exit': break
            if not cmd: continue
            cmd, *args = cmd.strip().split()
            if cmd == 'connect':
                print(f'--> Already connected to server({self.host}:{self.port}).')
                continue
            elif cmd == 'quit':
                return '-->' + Command.execute(cmd, host=self.host, port=self.port)
            print('-->', Command.execute(cmd, host=self.host, port=self.port))

