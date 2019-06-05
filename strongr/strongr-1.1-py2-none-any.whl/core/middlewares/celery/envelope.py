import celery
import strongr.core
import jsonpickle

class Envelope(celery.Task):
    def patch(self, celery_app, name, ignore_result):
        self.name = name
        self.app = celery_app
        # register ourselves with celery
        # this way celery knows about this command
        celery_app.tasks.register(self)
        #print('{} ignore result: {}'.format(name, ignore_result))
        self._ignore_result = ignore_result

    def run(self, command, *args, **kwargs):
        core = strongr.core.Core()

        command = jsonpickle.decode(command)

        result = core.command_router().handle_command(command)
        # ignore return value if flag is true
        # workaround from https://github.com/celery/celery/issues/1904
        if self._ignore_result:
            raise celery.exceptions.Ignore()
        return result
