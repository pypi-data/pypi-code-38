from marshmallow import ValidationError  # noqa, republishing


class UMongoError(Exception):
    pass


# class ValidationError(ValidationError, UMongoError):
#     pass


class AbstractDocumentError(UMongoError):
    pass


class DocumentDefinitionError(UMongoError):
    pass


class NoDBDefinedError(UMongoError):
    pass


class NotRegisteredDocumentError(UMongoError):
    pass


class AlreadyRegisteredDocumentError(UMongoError):
    pass


class BuilderNotDefinedError(UMongoError):
    pass


class UpdateError(UMongoError):
    pass


class DeleteError(UMongoError):
    pass


class MissingSchemaError(UMongoError):
    pass


class NotCreatedError(UMongoError):
    pass


class NoCollectionDefinedError(UMongoError):
    pass


class FieldNotLoadedError(UMongoError):
    pass


class NoCompatibleBuilderError(UMongoError):
    pass


class UnknownFieldInDBError(UMongoError):
    pass
