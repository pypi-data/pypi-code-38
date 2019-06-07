from .base import ResourceDetailBase, ResourceListBase
from .decorators import register
from .links import ResourceLink
from .manager import ModelResourceRegistry
from .models import ModelMixin, ModelResource, ModelResourceList


registry = ModelResourceRegistry()


__all__ = [
    'ResourceDetailBase',
    'ResourceListBase',
    'ModelMixin',
    'ModelResource',
    'ModelResourceList',
    'ResourceLink',
    'register',
    'registry'
]
