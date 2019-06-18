from rest_framework.exceptions import ValidationError

from .data import EnkelvoudigInformatieObject


class BackendException(ValidationError):
    def __init__(self, detail, create=False, update=False, retreive_single=False, delete=False, retreive_list=False, code=None):
        self.create = create
        self.update = update
        self.retreive_single = retreive_single
        self.delete = delete
        self.retreive_list = retreive_list

        super().__init__(detail, code)


class AbstractStorageBackend:
    exception_class = BackendException
    dataclass = EnkelvoudigInformatieObject
