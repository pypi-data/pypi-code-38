class Token:
    __base_form = '',
    __is_out_of_vocabulary = False
    __part_of_speech = ''
    __sentence = 0.0
    __sentiment = '' # Experimental
    __tag = ''
    __token_text = ''
    __positive = False
    __analysis_result = None

    def __init__(self, base_form, is_out_of_vocabulary, part_of_speech, sentence, sentiment, tag, token_text):
        self.__base_form = base_form
        self.__is_out_of_vocabulary = is_out_of_vocabulary
        self.__part_of_speech = part_of_speech
        self.__sentence = sentence
        self.__sentiment = sentiment
        self.__tag = tag
        self.__token_text = token_text

    def get_base_form(self):
        return self.__base_form

    def get_token_text(self):
        return self.__token_text

    def is_positive(self):
        return self.__positive

    def to_dict(self):
        """
        Devuelve los atributos del objeto en Diccionario de Python

        :return: [Dict] - Diccionario con los datos del token.
        """
        return {
            'base_form': self.__base_form,
            'is_out_of_vocabulary': self.__is_out_of_vocabulary,
            'part_of_speech': self.__part_of_speech,
            'sentence': self.__sentence,
            'sentiment': self.__sentiment,
            'tag': self.__tag,
            'token_text': self.__token_text,
            'positve': self.__positive,
            'analysis_result': self.__analysis_result
        }

    def set_theme_detected(self, theme, message):
        """
        Setea al token como un positivo en la busqueda. Asigna el mensaje y el tema 
        encontrado en el mismo.

        :theme: [String] - Tema / categoria detectada.

        :message: [String] - Mensaje de detección.
        """
        self.__positive = True
        self.__analysis_result = {
            'category_detected': theme,
            'alert_message': message
        }
