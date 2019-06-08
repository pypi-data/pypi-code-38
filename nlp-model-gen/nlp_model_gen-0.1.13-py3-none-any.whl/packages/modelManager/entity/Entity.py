class Entity:
    __text = ''
    __start = 0
    __end = 0
    __label = ''

    def __init__(self, text, start, end, label):
        self.__text = text
        self.__start = start
        self.__end = end
        self.__label = label

    def to_dict(self):
        """
        Retorna la entidad como un diccionario.

        :return: [Dict] - Diccionario con los datos de la entidad.
        """
        return {
            'text': self.__text,
            'start_pos': self.__start,
            'end_pos': self.__end,
            'label': self.__label
        }
        