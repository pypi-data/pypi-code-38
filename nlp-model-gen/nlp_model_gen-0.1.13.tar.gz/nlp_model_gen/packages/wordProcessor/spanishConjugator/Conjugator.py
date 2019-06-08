# @Vendors
import fnmatch
import copy
from terminaltables import AsciiTable

# @Helpers
from .helpers.presenteIndicativoHelper import presente_conj
from .helpers.preteritoPerfSimpleHelper import preterito_perf_simple_conj
from .helpers.preteritoImperfHelper import preterito_imperf_conj
from .helpers.futuroSimpleHelper import futuro_simple_conj
from .helpers.condicionalSimpleAHelper import condicional_simple_A_conj
from .helpers.condicionalSimpleBHelper import condicional_simple_B_conj
from .helpers.imperativoAHelper import imperativo_A_conj
from .helpers.imperativoBHelper import imperativo_B_conj
from .helpers.imperativoCHelper import imperativo_C_conj
from .helpers.participioHelper import participio
from .helpers.gerundioHelper import gerundio
from .helpers.irregularVerbGeneratorHelper import get_irregular_verbs

# Conjugator: provee diferentes funciones para conjugar verbos en español a los
# siguientes tiempos:
# - Indicativo
# --- Presente
# --- Preterito imperfecto
# --- Preterito perfecto
# --- Condicional
# --- Futuro
# - Subjuntivo
# --- Preterito imperfecto (2)
# - Imperativo (diferentes variaciones y adaptaciones al dialecto argentino)
class Conjugator:

    # <modo> valor numerico entero que define el modo de uso:
    # --> 0: dialecto argentino, se reemplaza la conjugación de la segunda persona
    # singular para adaptarlo al "voseo" caracteristico del dialecto.
    # --> != 0: dialecto general. Se deja como valor numerico y no como booleano
    # pensando en la posibilidad de adaptar el conjugador a nuevos modos.
    def __init__(self, mode, general_config, irregular_verb_groups_config, irregular_verb_exceptions_config):
        self.__mode = mode
        self.__configs = {
            'config': general_config,
            'irregular_verb_exceptions': {},
            'irregular_verb_groups': irregular_verb_groups_config,
            'irregular_verb_exceptions_config': irregular_verb_exceptions_config
        }
        get_irregular_verbs(self.__configs['irregular_verb_exceptions'], self.__mode, self.__configs)
   
    def set_mode(self, mode):
        self.__mode = mode

    def set_general_config(self, general_config):
        self.__configs['config'] = general_config
        self.__configs['irregular_verb_exceptions'] = {}
        get_irregular_verbs(self.__configs['irregular_verb_exceptions'], self.__mode, self.__configs)

    def set_irregular_verb_groups_config(self, irregular_verb_groups_config):
        self.__configs['irregular_verb_groups'] = irregular_verb_groups_config
        self.__configs['irregular_verb_exceptions'] = {}
        get_irregular_verbs(self.__configs['irregular_verb_exceptions'], self.__mode, self.__configs)

    def set_irregular_verb_exceptions_config(self, irregular_verb_exceptions_config):
        self.__configs['irregular_verb_exceptions_config'] = irregular_verb_exceptions_config
        self.__configs['irregular_verb_exceptions'] = {}
        get_irregular_verbs(self.__configs['irregular_verb_exceptions'], self.__mode, self.__configs)

    def __apply_conjugation(self, verb, conjugation):
        return conjugation(verb, False, self.__mode, self.__configs)

    # Crea un diccionario de conjugación aplicando todos los helpers de conjugación,
    # en este caso no se utiliza ninguna de las excepciones de verbos completamente
    # irregulares.
    def generar_conjugaciones(self, verb):
        return {
            'inf': [verb],
            'ger': self.__apply_conjugation(verb, gerundio),
            'part': self.__apply_conjugation(verb, participio),
            'pres': self.__apply_conjugation(verb, presente_conj),
            'pret_perf': self.__apply_conjugation(verb, preterito_perf_simple_conj),
            'pret_imperf': self.__apply_conjugation(verb, preterito_imperf_conj),
            'fut': self.__apply_conjugation(verb, futuro_simple_conj),
            'impA': self.__apply_conjugation(verb, imperativo_A_conj),
            'impB': self.__apply_conjugation(verb, imperativo_B_conj),
            'impC': self.__apply_conjugation(verb, imperativo_C_conj),
            'condA': self.__apply_conjugation(verb, condicional_simple_A_conj),
            'condB': self.__apply_conjugation(verb, condicional_simple_B_conj)
        }
    
    # Crea un diccionario de conjugación a partir de la conjugación para un verbo irregular
    # dado. Si dicho verbo irregular resultase un sufijo del verbo solicitado, se 
    # concatenará la base del verbo con el sufijo conjugado.
    def __generar_dict_irregular_concatenado(self, key, verb):
        if key == '':
            conjugation = copy.deepcopy(self.__configs['irregular_verb_exceptions'][verb])
            base_verb = ''
        else:
            conjugation = copy.deepcopy(self.__configs['irregular_verb_exceptions'][key])
            base_verb = verb.replace(key, '')
        for key in conjugation.keys():
            i = 0
            while i < len(conjugation[key]):
                if conjugation[key][i] != '':
                    conjugation[key][i] = base_verb + conjugation[key][i]
                i += 1
        return conjugation

    # Genera un diccionario con el verbo pasado como parametro conjugado en los
    # distintos tiempos disponibles.
    # <verb> : debe ser una cadena de caracteres finalizada en uno de {ar, er, ir,
    # ár, ér, ír}. De no ser así se devuelve un diccionario vacio.
    def __generar_diccionario_conjugacion(self, verb):
        if not any(fnmatch.fnmatch(verb, suffix) for suffix in self.__configs['config']['verb_suffixes']):
            return {}
        key = self.__extract_key(verb)
        if key is not None:
            return self.__generar_dict_irregular_concatenado(key, verb)
        else:
            return self.generar_conjugaciones(verb)

    # Verifica que un verbo no termine con la clave de uno de los verbos irregulares
    # declarados en el diccionario de verbos irregulares. Si efectivamente es así,
    # devuelve None.
    # En caso contrario si el verbo coincide completamente (no es subcadena) devuelve
    # una clave vacia. O si es una subcadena, devuelve la subcadena que ha
    # matcheado.
    def __extract_key(self, verb):
        for key in self.__configs['irregular_verb_exceptions']:
            if fnmatch.fnmatch(verb, '*' + key) and key not in self.__configs['config']['irregular_suffix_exceptions']:
                if key != verb:
                    return key
                else:
                    return ''
        return None

    # Devuelve un diccionario con el formato estándar y las posiciones reservadas,
    # pero con cadenas vacias. Se utiliza para cuando table_view recibe un
    # verbo no válido.
    def __empty_dict(self):
        return self.__configs['config']['empty_conj_dict']

    # Construye la primera fila de la tabla de conjugación
    def __contruir_primera_fila(self, conjugation):
        return [
            self.__configs['config']['table_headers'][0],
            [self.__configs['config']['row_headers'][0][0], conjugation['pres'][0], conjugation['pret_imperf'][0], conjugation['pret_perf'][0], conjugation['condA'][0]],
            [self.__configs['config']['row_headers'][0][1], conjugation['pres'][1], conjugation['pret_imperf'][1], conjugation['pret_perf'][1], conjugation['condA'][1]],
            [self.__configs['config']['row_headers'][0][2], conjugation['pres'][2], conjugation['pret_imperf'][2], conjugation['pret_perf'][2], conjugation['condA'][2]],
            [self.__configs['config']['row_headers'][0][3], conjugation['pres'][3], conjugation['pret_imperf'][3], conjugation['pret_perf'][3], conjugation['condA'][3]],
            [self.__configs['config']['row_headers'][0][4], conjugation['pres'][4], conjugation['pret_imperf'][4], conjugation['pret_perf'][4], conjugation['condA'][4]],
            [self.__configs['config']['row_headers'][0][5], conjugation['pres'][5], conjugation['pret_imperf'][5], conjugation['pret_perf'][5], conjugation['condA'][5]]
        ]

    # Construye la segunda fila de la tabla de conjugación
    def __construir_segunda_fila(self, conjugation):
        return [
            self.__configs['config']['table_headers'][1],
            [self.__configs['config']['row_headers'][0][0], conjugation['fut'][0], conjugation['condB'][0], conjugation['impA'][0], conjugation['impB'][0], conjugation['impC'][0]],
            [self.__configs['config']['row_headers'][0][1], conjugation['fut'][1], conjugation['condB'][1], conjugation['impA'][1], conjugation['impB'][1], conjugation['impC'][1]],
            [self.__configs['config']['row_headers'][0][2], conjugation['fut'][2], conjugation['condB'][2], conjugation['impA'][2], conjugation['impB'][2], conjugation['impC'][2]],
            [self.__configs['config']['row_headers'][0][3], conjugation['fut'][3], conjugation['condB'][3], conjugation['impA'][3], conjugation['impB'][3], conjugation['impC'][3]],
            [self.__configs['config']['row_headers'][0][4], conjugation['fut'][4], conjugation['condB'][4], conjugation['impA'][4], conjugation['impB'][4], conjugation['impC'][4]],
            [self.__configs['config']['row_headers'][0][5], conjugation['fut'][5], conjugation['condB'][5], conjugation['impA'][5], conjugation['impB'][5], conjugation['impC'][5]]
        ]

    # Construye la tercera fila de la tabla de conjugación
    def __construir_tercera_fila(self, conjugation):
        return [
            self.__configs['config']['table_headers'][2],
            [self.__configs['config']['row_headers'][1][0], conjugation['inf'][0]],
            [self.__configs['config']['row_headers'][1][1], conjugation['ger'][0]],
            [self.__configs['config']['row_headers'][1][2], conjugation['part'][0]],
            [self.__configs['config']['row_headers'][1][3], conjugation['part'][1]],
            [self.__configs['config']['row_headers'][1][4], conjugation['part'][2]]
        ]

    # Recibe un verbo, lo conjuga y devuelve por consola una tabla con las
    # conjugaciones obtenidas. Utiliza la libreria 'terminaltables'.
    # <verb> : debe ser una cadena de caracteres finalizada en uno de {ar, er, ir,
    # ár, ér, ír}. De no ser así se devuelve una tabla vacía.
    def table_view(self, verb):
        conjugation = self.__generar_diccionario_conjugacion(verb)
        if conjugation == {}:
            conjugation = self.__empty_dict()
        table_data_1 = self.__contruir_primera_fila(conjugation)
        table_01 = AsciiTable(table_data_1)
        table_data_2 = self.__construir_segunda_fila(conjugation)
        table_02 = AsciiTable(table_data_2)
        table_data_3 = self.__construir_tercera_fila(conjugation)
        table_03 = AsciiTable(table_data_3)
        print(table_03.table)
        print('')
        print(table_01.table)
        print('')
        print(table_02.table)
