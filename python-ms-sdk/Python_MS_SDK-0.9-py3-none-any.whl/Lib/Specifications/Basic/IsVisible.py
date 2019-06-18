from ms_sdk.Lib.Specifications.Basic.FilterSpecification import FilterSpecification


class IsVisible(FilterSpecification):

    def isSatisfiedBy(self, entity):
        """
        :param Entity entity:
        :rtype bool:
        """
        if hasattr(entity, 'visible'):
            return bool(entity.visible)

        print("Property 'visible' does not exist in class" + str(entity))