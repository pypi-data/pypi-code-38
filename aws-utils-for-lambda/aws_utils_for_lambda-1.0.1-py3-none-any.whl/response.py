import sys
import json
import traceback


class ResponseObject:
    def __init__(self, *args, **kwargs):
        exception = kwargs.get('exception')
        self.traceback = exception.__traceback__ if int(sys.version[0]) == 3 and exception is not None else None
        self.data = kwargs.get('data')
        self.success = False if exception else True
        self.output_format = kwargs.get('output_format') if kwargs.get('output_format') else 'dict'
        self.error = type(exception).__name__ if exception else None
        self.error_message = str(exception) if exception else None
        self.full_response = kwargs.get('full_response')
        self.short_traceback = traceback.format_tb(self.traceback) if exception else None
        self.full_traceback = traceback.format_exception(etype=type(exception),
                                                         value=exception,
                                                         tb=self.traceback) if exception else None

    def response(self):
        if self.output_format == 'json':
            j_data = json.dumps(self.__dict__, default=str)
            return j_data
        elif self.output_format == 'dict':
            return self.__dict__
        return self.__dict__
