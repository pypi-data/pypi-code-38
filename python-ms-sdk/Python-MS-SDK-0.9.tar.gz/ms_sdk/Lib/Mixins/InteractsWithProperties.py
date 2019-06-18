

class InteractsWithPropertiesMixin:

    entity = {}

    def setPropertyList(self, data):
        """
        :param dict data:
        """
        for optionKey, optionValue in data.items():
            # For reserved vars '_varname'
            if hasattr(self, '_' + optionKey):
                setattr(self, '_' + optionKey, optionValue)
            else:
                setattr(self, optionKey, optionValue)
