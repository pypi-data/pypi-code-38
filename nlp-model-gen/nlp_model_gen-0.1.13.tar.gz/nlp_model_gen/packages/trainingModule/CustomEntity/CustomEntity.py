class CustomEntity:
    def __init__(self, name, description):
        self.__name = name
        self.__description = description

    def get_name(self):
        return self.__name

    def get_description(self):
        return self.__description

    def set_description(self, description):
        self.__description = description

    def to_dict(self):
        """
        Obtiene un diccionario a partir de los datos de la entidad.

        :return: [Dict] - Diccionario con los datos de la entidad
        """
        return {
            'name': self.get_name(),
            'description': self.get_description()
        }
