# @Vendors
from spacy.symbols import ORTH, LEMMA, POS, TAG, SHAPE #pylint: disable=no-name-in-module

# @Constants
from nlp_model_gen.constants.constants import (
    TOKEN_RULES_GEN_NOUN_SING_TAG,
    TOKEN_RULES_GEN_NOUN_PLUR_TAG,
    DEFAULT_REPLACE_WILDCARD, 
    TOKEN_RULES_GEN_NOUN, 
    TOKEN_RULES_GEN_VERB, 
    TOKEN_RULES_GEN_VERB_CFG
)

# @Classes
from nlp_model_gen.packages.wordProcessor.WordProcessorController import WordProcessorController
from nlp_model_gen.packages.logger.Logger import Logger

# @Logger colors
from nlp_model_gen.packages.logger.assets.logColors import HIGHLIGHT_COLOR

# @Resourses
from ..packageUtils.token_tags import TOKEN_TAGS

class TokenGenerator:
    __word_processor = None

    def __init__(self):
        self.__word_processor = WordProcessorController()

    def __get_tag_key(self, person, time_key):
        """
        Obtiene el elemento un determinado key y persona.

        :person: [int] - Indice de la persona (0 - 5).

        :time_key: [String] - Tiempo verbal

        :return: [String] - Tag correspondiente al tiempo de conjugación para la persona.
        """
        try:
            key = TOKEN_RULES_GEN_VERB_CFG[time_key]['time_keys'][person]
            tag_key_frame = TOKEN_RULES_GEN_VERB_CFG[time_key]['tag_keys'][person]
            tag_key = tag_key_frame.replace(DEFAULT_REPLACE_WILDCARD, key)
            return TOKEN_TAGS[tag_key]
        except:
            return ''

    def __get_shape(self, token):
        """
        Da la forma de la palabra pasada como parametro. Por ejemplo si la
        palabra pasada como parametro es 'Hola' devuelve 'Xxxx'

        :token: [String] - Palabra a partir de la cual se quiere obtener la forma.

        :return: [String] - Cadena de caracteres que contiene la forma de la palabra
        pasada como parametro.
        """
        shape_string = ''
        for char in token:
            if not str(char).isspace():
                shape_string += 'x'
            else:
                shape_string += ' '
        return shape_string

    def __get_verb_token_rule(self, verb, base_verb, person, time_key):
        """
        Genera una regla para el tokenizer con la forma:

        {<variation>: [{ ORTH:<variation>, 
                         LEMMA:<palabra raíz a la que refiere>,
                         POS:<part of speech (verbo, sust, etc)>,
                         TAG:<tag (profundiza el part of speech)>,
                         SHAPE:<xxxxxxxxx (Ej. para 'variation')>
                       }]
        }

        Donde en lugar de utilizar una variación utiliza el termino escrito
        correctamente.

        :verb: [String] - Verbo conjugado.

        :base_verb: [String] - Verbo raíz.

        :person: [int] - Indice de la persona (0 - 5).

        :time_key: [String] - Clave del tiempo verbal de la conjugación.

        :return: [Dict] - Lista de objetos de congifuración para cada conjugación disponible.
        """
        return {
            verb: [{
                ORTH: verb,
                LEMMA: base_verb,
                POS: TOKEN_RULES_GEN_VERB,
                TAG: self.__get_tag_key(person, time_key),
                SHAPE: self.__get_shape(verb)
            }]
        }

    def __get_noun_token_rule(self, noun, base_noun, tag):
        """
        Genera una regla para el tokenizer con la forma:

        {<variation>: [{ ORTH:<variation>, 
                         LEMMA:<palabra raíz a la que refiere>,
                         POS:<part of speech (verbo, sust, etc)>,
                         TAG:<tag (profundiza el part of speech)>,
                         SHAPE:<xxxxxxxxx (Ej. para 'variation')>
                       }]
        }

        Donde en lugar de utilizar una variación utiliza el termino escrito
        correctamente.

        :noun: [String] - Verbo conjugado.

        :base_noun: [String] - Verbo raíz.

        :tag: [String] - Tag del sustantivo.

        :return: [Dict] - Lista de objetos de congifuración para cada conjugación disponible.
        """
        return {
            noun: [{
                ORTH: noun,
                LEMMA: base_noun,
                POS: TOKEN_RULES_GEN_NOUN,
                TAG: tag,
                SHAPE: self.__get_shape(noun)
            }]
        }

    def __create_custom_verb_token_rules(self, verb, base_verb, person, time_key, max_dist):
        """
        A partir de un verbo conjugado, utiliza el modulo WordProcessor para deformarlo. 
        Para cada deformación que cumpla con la distancia máxima deseada, se crea una regla.

        :verb: [String] - Cadena de caracteres con la forma "bien escrita" de la
        palabra a deformar.

        :base_verb: [String] - Forma base de la palabra (Ej. vende --> vender)

        :person: [int] - Indice de la persona (0 - 5)

        :time_key: [String] - Clave del tiempo verbal.

        :max_dist: Distancia de levenshtein máxima para que una variación
        de una palabra sea tomada como válida.
        """
        Logger.log('L-0014', [{'text': verb, 'color': HIGHLIGHT_COLOR}])
        fuzzy_token_set = self.__word_processor.get_fuzzy_set(verb, max_dist)
        tokenizer_exceptions_set = list([])
        for fuzzy_token in fuzzy_token_set:
            token_exception = self.__get_verb_token_rule(fuzzy_token, base_verb, person, time_key)
            tokenizer_exceptions_set.append(token_exception)
        return tokenizer_exceptions_set

    def __create_custom_noun_token_rules(self, noun, base_noun, max_dist, is_plural=False):
        """
        A partir de un sustantivo crea un set de reglas para el tokenizer. 

        :noun: [String] - Sustantivo.

        :base_noun: [String] - Palabra base (lemma).

        :max_dist: [int] - Distancia de demerau levenshtein máxima.

        :is_plural: [bool] - True si la palabra es plural. 
        """
        Logger.log('L-0015', [{'text': noun, 'color': HIGHLIGHT_COLOR}])
        fuzzy_set = self.__word_processor.get_fuzzy_set(noun, max_dist)
        tag = TOKEN_RULES_GEN_NOUN_SING_TAG if not is_plural else TOKEN_RULES_GEN_NOUN_PLUR_TAG
        noun_rule_set = list([])
        for fuzzy_token in fuzzy_set:
            noun_rule_set.append(self.__get_noun_token_rule(fuzzy_token, base_noun, tag))
        return noun_rule_set

    def generate_verb_rules_set(self, infinitive, max_dist):
        """
        A partir del verbo recibido genera las conjugaciones posibles utilizando 
        el conjugador y luego el generador de terminos fuzzy. Finalmente, retorna un 
        diccionario con las excepciones al tokenizer requeridas.

        :infinitive: [String] - Verbo en infinitivo que debe ser conjugado. Debe ser una
        cadena de caracteres terminada en uno de {'*ar', '*er', '*ir', '*ár',
        '*ér', '*ír'}

        :max_dist: [int] - Distancia de demerau_levenshtein máxima que se admite en las
        deformaciones.

        :return: [Dict] - Diccionario con todas las excepciones al conjugador generadas a 
        partir del verbo, sus conjugaciones y las deformaciones realizadas.
        """
        conj_dict = self.__word_processor.conjugate_verb(infinitive)
        verb_rules_dict = dict({})
        for key in conj_dict.keys():
            for index, verb in enumerate(conj_dict[key]):
                if verb != '':
                    verb_rules_dict[verb] = self.__create_custom_verb_token_rules(verb, infinitive, index, key, max_dist)
        return verb_rules_dict

    def generate_noun_rules_set(self, singular, max_dist):
        """
        A partir del sustantivo recibido obtiene su forma plural y deformaciones utilizando 
        el procesador de sutantivos y luego el generador de terminos fuzzy. Finalmente, retorna un 
        diccionario con las excepciones al tokenizer requeridas.

        :infinitive: [String] - Sustantivo a llevar a plural y deformar.

        :max_dist: [int] - Distancia de demerau_levenshtein máxima que se admite en las
        deformaciones.

        :return: [Dict] - Diccionario con todas las excepciones al conjugador generadas a 
        partir del verbo, sus conjugaciones y las deformaciones realizadas.
        """
        noun_rules_dict = dict({})
        noun_rules_dict[singular] = self.__create_custom_noun_token_rules(singular, singular, max_dist, False)
        plural_form = self.__word_processor.get_plural(singular)
        if plural_form != '':
            noun_rules_dict[plural_form] = self.__create_custom_noun_token_rules(plural_form, singular, max_dist, True)
        return noun_rules_dict
