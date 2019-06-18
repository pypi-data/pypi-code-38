from ms_sdk.Entities.Entity import Entity
from ms_sdk.Lib.Mixins.InteractsWithAttributes import InteractsWithAttributesMixin


class Document(Entity, InteractsWithAttributesMixin):

    id = None
    urlCode = None

    attributes = None
    functionalName = None



