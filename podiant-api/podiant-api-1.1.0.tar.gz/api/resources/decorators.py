def register(model):
    """
    Register the given model class and wrapped ModelResource class with
    registry::

        @register(Author)
        class AuthorResource(resources.ModelResource):
            pass
    """

    from .models import ModelResource, ModelResourceList
    from . import registry

    def _model_resource_wrapper(mixin_class):
        detail_class = type(
            '%sResource' % model.__name__,
            (mixin_class, ModelResource),
            {}
        )

        list_class = type(
            '%sResourceList' % model.__name__,
            (mixin_class, ModelResourceList),
            {}
        )

        registry.register(model, list_class, detail_class)
        return detail_class

    return _model_resource_wrapper
