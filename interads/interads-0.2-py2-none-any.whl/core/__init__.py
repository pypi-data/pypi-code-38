import types
import inject as injection

class ComponentContainer(object):
    """
    Container bootstraps some service which are injected directly
    For now we only support IoC
    """
    _services = {}

    def bind(self, cls, instance_or_callable):
        """
        Declare Singleton service for
        :param cls:
        :param instance_or_callable:
        :return:
        """
        self._services[cls] = instance_or_callable

    def configure(self):
        """Finalize bootstrapping"""

        def inject_binder(binder):
            """
            Bind service
            :type binder: inject.Binder
            :param binder: Binding service class
            :param core: Concrete class or lambda
            :return:
            """
            for cls, instance in self._services.iteritems():
                if isinstance(instance, types.LambdaType):
                    binder.bind_to_provider(cls, instance)
                else:
                    binder.bind(cls, instance)

        injection.configure(inject_binder)

