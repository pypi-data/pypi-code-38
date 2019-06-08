class Analyzer:
    def __init__(self, rule_set, exceptions_set):
        self.__rule_set = rule_set
        self.__exceptions_set = exceptions_set

    def validate_exception(self, token):
        """
        Valida que no exista una excepción activa para el token detectado.

        :token: [Token] - Token detectado.

        :return: [boolean] - True si se ha detectado una excepción activa,
        False en caso contrario.
        """
        for analyzer_exception in self.__exceptions_set:
            if analyzer_exception.check_exception(token.get_token_text(), token.get_base_form()):
                return False
        return True

    def analyze_token(self, token):
        """
        Utiliza un rule set para analizar un token. Si el token analizado
        se detecta como un positivo, se actualiza el mismo para indicar la
        detección.

        :token: [Token] - Token a a analizar.
        """
        if self.__rule_set is None:
            return
        for category in self.__rule_set:
            if token.get_base_form() in category['lemma_list'] and self.validate_exception(token):
                token.set_theme_detected(category['identifier'], category['alert_message'])
                return

    def classify_token(self, token):
        """
        Devuelve la clasificación de un token.

        :token: [SpacyToken] - Token a analizar.

        :return: [Dict] - Diccionario con el la clasificación y su detalle.
        """
        return {
            'orth': token.orth_,
            'type': token.pos_
        }
