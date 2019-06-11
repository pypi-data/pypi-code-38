import django.dispatch

rebotics_update = django.dispatch.Signal(
    providing_args=['component', 'status', 'body']
)
processing_succeed = django.dispatch.Signal(
    providing_args=['processing_id', 'body']
)
processing_started = django.dispatch.Signal(
    providing_args=['processing_id', 'body']
)
processing_failed = django.dispatch.Signal(
    providing_args=['processing_id', 'body']
)
processing_update_received = django.dispatch.Signal(
    providing_args=['processing_id', 'status', 'body']
)


class SignalEmitter(object):
    def __init__(self, component, status, body, request):
        self.body = body
        self.status = status
        self.component = component
        self.request = request

    def emit(self):
        rebotics_update.send_robust(
            sender=self,
            component=self.component,
            status=self.status,
            body=self.body
        )


class ProcessingSignalEmitter(SignalEmitter):
    started = processing_started
    succeed = processing_succeed
    failed = processing_failed
    received = processing_update_received

    def emit(self):
        super(ProcessingSignalEmitter, self).emit()
        processing_id = self.body['id']

        self.received.send_robust(
            sender=self,
            processing_id=processing_id,
            status=self.status,
            body=self.body
        )

        getattr(self, self.status).send_robust(sender=self, processing_id=processing_id, body=self.body)


def emitter_factory(component, status, body, request):
    components = {
        'processing': ProcessingSignalEmitter,
        'internal': SignalEmitter,
    }
    emitter = components.get(component, SignalEmitter)

    return emitter(component, status, body, request)
