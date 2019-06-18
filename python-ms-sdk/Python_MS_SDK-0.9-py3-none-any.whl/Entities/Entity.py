from ms_sdk.Lib.Mixins.InteractsWithProperties import InteractsWithPropertiesMixin


class Entity(InteractsWithPropertiesMixin):

    def __init__(self, array):
        """
        Entity constructor.
        :param array:
        """
        if not array:
            return self

        return self.setPropertyList(array)

    def asArray(self):
        """
        :rtype: list
        """
        properties = {}

        for itemKey, itemValue in self:
            if itemKey == 'properties':
                continue
            properties.update({itemKey: itemValue})

        return properties.update(self.properties)

    # def getType(self):
    #     stack = inspect.stack()
    #     the_class = stack[1][0].f_locals["self"].__class__
    #
    #     print(__class__)
    #     return the_class
