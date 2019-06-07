from . import service_pb2_grpc, service_pb2
from datetime import datetime
from pathlib import Path
from . import logger
import pickle


class Controller(service_pb2_grpc.ControllerServicer):
    def __init__(self, dump_path):
        self.start_time = datetime.now()
        self.is_active = True
        self.is_quit = False
        self.dump_path = dump_path
        self.task_index = 0
        self.task_set = {}
        self.task_list = []

    def SendStatus(self, request, context):
        if self.is_quit: return service_pb2.SendStatusResponse(command='quit', tasks=pickle.dumps([]))
        # logging
        for msg in pickle.loads(request.logs):
            logger._logging(msg)
        # Clear tasks
        for code in pickle.loads(request.completed_tasks):
            del self.task_set[code]
        # Append tasks
        for task in pickle.loads(request.tasks):
            self.task_set[self.task_index] = {'fn': task}
            self.task_list.append(self.task_index)
            self.task_index += 1
        logger.system(f'Status - task_count= {len(self.task_list)}  task_total= {self.task_index}', 'Server')
        # Return tasks
        if self.is_active and request.free_count > 0:
            task_codes = self.task_list[:request.free_count]
            tasks = []
            for code in task_codes:
                tasks.append((code, self.task_set[code]['fn']))
            self.task_list = self.task_list[request.free_count:]
            return service_pb2.SendStatusResponse(command='add', tasks=pickle.dumps(tasks))
        else: return service_pb2.SendStatusResponse(command='pass', tasks=pickle.dumps([]))

    def SendCommand(self, request, context):
        logger.system(f'Receive command - {request.command}', 'Server')
        if request.command == 'start':
            self.is_active = True
            return service_pb2.SendCommandResponse(info='Start successfully.')
        elif request.command == 'stop':
            self.is_active = False
            return service_pb2.SendCommandResponse(info='Stop successfully.')
        elif request.command == 'save':
            dump_file = Path(self.dump_path) / f'{self.start_time.strftime("%Y-%m-%d %H-%M-%S")}.data'
            with open(dump_file, 'wb') as f:
                pickle.dump(self.task_set, f)
            return service_pb2.SendCommandResponse(info=f'Save successfully! file path: {dump_file.resolve()}.')
        elif request.command == 'quit':
            self.is_active = False
            self.is_quit = True
            return service_pb2.SendCommandResponse(info='Quit successfully! please wait a few seconds...')
        elif request.command == 'task_total':
            return service_pb2.SendCommandResponse(info=str(self.task_index))
        elif request.command == 'task_count':
            return service_pb2.SendCommandResponse(info=str(len(self.task_list)))
        elif request.command == 'start_time':
            return service_pb2.SendCommandResponse(info=str(self.start_time))
        return service_pb2.SendCommandResponse(info='')
