class Extension:
    def __init__(self, data):
        """
        Accepts a row from extensions.csv and assigns values to properties.
        """
        self.id = data['Id']
        self.category = data['Category']
        self.core = data['Core'] == 'true'

    def as_dict(self):
        """
        Returns the object's properties as a dictionary.

        This method is defined to match the method in `ExtensionVersion`.
        """
        return self.__dict__
