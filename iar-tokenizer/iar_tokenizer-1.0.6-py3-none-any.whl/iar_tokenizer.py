# -*- coding: utf-8 -*-
u"""Proporciona la clase Segmentador, que segmenta cadenas de caracteres en frases y palabras.

La clase Segmentador contiene únicamente métodos estáticos. Estos métodos toman un texto (o una lista de
textos) y lo segmentan según diversos caracteres y cumpliendo diversas condiciones. Los dos métodos
principales son segmenta_por_frases y segmenta_por_palabras, y el resto se utilizan como métodos auxiliares de
los dos métodos principales (aunque también se pueden utilizar los métodos auxiliares de forma independiente).
"""

from nltk.tokenize import RegexpTokenizer


class Tokenizer:
    u"""Esta clase segmenta en tokens (frases o palabras) un texto expresado como una cadena de caractereres.

    No contiene atributos, con lo que todos sus métodos son estáticos.
    """

    def __init__(self):
        pass

    @staticmethod
    def segmenta_estructurado(texto, elimina_separadores=False, elimina_separadores_blancos=True,
                              parentesis_segmentan_frases=False,
                              segmenta_por_guiones_internos=True, segmenta_por_guiones_externos=True,
                              adjunta_separadores=False, agrupa_separadores=False):
        u"""Se toma un texto de entrada y se devuelve segmentado de forma estructurada en párrafos,
        frases y palabras (o signos de puntuación).

        Los separadores (signos de puntuación) se eliminan o no según el parámetro.
        Y en caso de no eliminarse, cabe la posibilidad de que se adjunten como parte (inicial o final) de
        una palabra, o de que se dejen como tokens independientes.

        :type texto: unicode
        :param texto: La cadena de caracteres que conforma el texto de entrada.
        :type elimina_separadores: bool
        :param elimina_separadores: Si está a True, los separadores se eliminan del resultado.
            Si está a False, dichos separadores se incluyen como tokens independientes en el listado final.
        :type elimina_separadores_blancos: bool
        :param elimina_separadores_blancos: Lo mismo que elimina_separadores pero en específico para los que
            son separadores blancos.
        :type parentesis_segmentan_frases: bool
        :param parentesis_segmentan_frases: Si está a True, también se usan los "paréntesis" ("()[]{}") para
            segmentar frases.
            Si está a False, dichos caracteres no segmentan frases.
        :type segmenta_por_guiones_internos: bool
        :param segmenta_por_guiones_internos: Si está a True, se segmenta por guiones completamente
            rodeados de caracteres no blancos (lo cual separa cosas como "judeo-masónica").
        :type segmenta_por_guiones_externos: bool
        :param segmenta_por_guiones_externos: Si está a True, se segmenta por guiones no completamente
            rodeados de caracteres no blancos (lo cual separa el guion de un prefijo, pero también aquellos
            guiones que funcionan como si fueran paréntesis).
        :type adjunta_separadores: bool
        :param adjunta_separadores: Si es False, los signos ortográficos se dan como tokens independientes.
            Si está a True los signos ortográficos no se colocan como tokens independientes sino que se
            adjuntan al siguiente/anterior token según corresponda: los signos de apertura se añaden al
            siguiente y los de cierre y pausa se adjuntan al anterior.
        :type agrupa_separadores: bool
        :param agrupa_separadores: Solo afecta si adjunta_separadores es True. En dicho caso,
            si este parámetro está a True, cada frase no es un simple unicode, sino que es una lista de
            unicodes: signos de apertura, texto y signos de cierre de frase. Si este parámetro está a
            False, entonces se devuelve un listado de unicodes, que pueden ser el texto de la frase o de
            los signos de apertura/cierre.
        :rtype: [unicode]
        :return: Una lista de cadenas de texto, cada una representando a una frase o a un separador.
        """
        if not texto:
            return []
        texto_estructurado = []
        for parrafo_txt in Tokenizer.segmenta_por_parrafos(texto):
            # Primero segmentamos según caracteres que siempre dividen palabras (y frases).
            tokens = Tokenizer. \
                segmenta_por_frases(parrafo_txt,
                                    elimina_separadores=elimina_separadores,
                                    elimina_separadores_blancos=elimina_separadores_blancos,
                                    incluye_parentesis=parentesis_segmentan_frases,
                                    adjunta_separadores=adjunta_separadores,
                                    agrupa_separadores=agrupa_separadores)
            # Ahora mismo podemos estar en dos casos:
            # - Si elimina_separadores es falso y se adjuntan y agrupan los separadores, tokens es una
            # lista (de frases) de listas de tokens (unicodes que representan el texto de la frase o un
            # segmentador de frase inicial o final).
            # - Si los separadores se eliminan o no se adjuntan como agrupaciones, tokens es una lista de
            # frases (unicodes) que contendrán o no los separadores a su inicio/fin según los parámetros.
            parrafo = []
            # Si no eliminamos los separadores, y además los adjuntamos agrupándolos, la frase será una
            # lista de unicode. En cualquier otro caso, frase será un unicode.
            if elimina_separadores or not adjunta_separadores or not agrupa_separadores:
                for frase in tokens:
                    frase_tokenizada = Tokenizer.\
                        segmenta_por_palabras([frase],
                                              elimina_separadores=elimina_separadores,
                                              adjunta_separadores=adjunta_separadores,
                                              segmenta_por_guiones_internos=segmenta_por_guiones_internos,
                                              segmenta_por_guiones_externos=segmenta_por_guiones_externos,
                                              agrupa_separadores=agrupa_separadores)
                    if frase_tokenizada:
                        parrafo.append(frase_tokenizada)
            else:
                for frase in tokens:
                    frase_tokenizada = Tokenizer. \
                        segmenta_por_palabras(frase,
                                              elimina_separadores=elimina_separadores,
                                              adjunta_separadores=False,
                                              segmenta_por_guiones_internos=segmenta_por_guiones_internos,
                                              segmenta_por_guiones_externos=segmenta_por_guiones_externos,
                                              agrupa_separadores=agrupa_separadores)
                    if frase_tokenizada:
                        parrafo.append(frase_tokenizada)
            if parrafo:
                texto_estructurado.append(parrafo)
        return texto_estructurado

    @staticmethod
    def segmenta_por_parrafos(texto):
        u"""Se toma un texto de entrada y se devuelve segmentado por párrafos como una lista de strings.

        Los separadores de párrafos se eliminan. Se considera que un párrafo lo constituye texto rodeado de
        blancos (o inicio/final de texto) que incluyen al menos un salto de línea.

        :type texto: unicode
        :param texto: La cadena de caracteres que conforma el texto de entrada.
        :rtype: [unicode]
        :return: una list con los párrafos (que son strings unicode) que resultan tras segmentar.
        """
        regex = r'(?:[^\n\r]+)'
        segmentador = RegexpTokenizer(regex)
        return [token.strip() for token in segmentador.tokenize(texto) if token.strip()]

    @staticmethod
    def segmenta_por_frases(texto, elimina_separadores=False, elimina_separadores_blancos=True,
                            incluye_parentesis=False, adjunta_separadores=True, agrupa_separadores=False):
        u"""Se toma un texto de entrada y se devuelve segmentado por frases como una lista de strings.

        Los separadores de frases se eliminan o no según el parámetro. Y en caso de no eliminarse, cabe la
        posibilidad de que se adjunten como parte (inicial o final) de una frase, o de que se dejen como
        tokens independientes al inicio o fin de una frase.

        Se considera que una frase la constituye una cadena de texto que termina en un punto "segmentador" o
        en alguno de los segmentadores no ambiguos (tabuladores o signos de exclamación, interrogación...).
        Por lo tanto, segmentar por frases equivalente a aplicar la segmentación no ambigua, y después la
        segmentación de puntos.

        :type texto: unicode
        :param texto: La cadena de caracteres que conforma el texto de entrada.
        :type elimina_separadores: bool
        :param elimina_separadores: Si está a True, los separadores se eliminan del resultado.
            Si está a False, dichos separadores se incluyen como tokens independientes en el listado final.
        :type elimina_separadores_blancos: bool
        :param elimina_separadores_blancos: Lo mismo que elimina_separadores pero en específico para los que
            son separadores blancos.
        :type incluye_parentesis: bool
        :param incluye_parentesis: Si está a True, también se usan los "paréntesis" ("()[]{}") para segmentar.
            Si está a False, dichos caracteres no segmentan nada.
        :type adjunta_separadores: bool
        :param adjunta_separadores: Si es False, los signos ortográficos se dan como tokens independientes.
            Si está a True los signos ortográficos no se colocan como tokens independientes sino que se
            adjuntan al siguiente/anterior token según corresponda: los signos de apertura se añaden al
            siguiente y los de cierre y pausa se adjuntan al anterior.
        :type agrupa_separadores: bool
        :param agrupa_separadores: Solo afecta si adjunta_separadores es True. En dicho caso,
            si este parámetro está a True, cada frase no es un simple unicode, sino que es una lista de
            unicodes: signos de apertura, texto y signos de cierre de frase. Si este parámetro está a
            False, entonces se devuelve un listado de unicodes, que pueden ser el texto de la frase o de
            los signos de apertura/cierre.
        :rtype: [unicode]
        :return: Una lista de cadenas de texto, cada una representando a una frase o a un separador.
        """
        if not texto:
            return []
        # Se prefiere el uso de los puntos suspensivos como un único carácter porque facilita el
        # procesado al consistir, como todos los demás signos de puntuación, en un único carácter.
        texto = texto.replace(u'...', u'…')
        # Primero segmentamos según caracteres que siempre dividen palabras (y frases).
        tokens = Tokenizer.segmenta_por_no_ambiguos([texto],
                                                    elimina_separadores=elimina_separadores,
                                                    elimina_separadores_blancos=elimina_separadores_blancos,
                                                    incluye_parentesis=incluye_parentesis)
        # Después por dos puntos.
        tokens = Tokenizer.segmenta_por_dos_puntos(tokens, elimina_separadores=elimina_separadores)
        # Después por puntos.
        tokens = Tokenizer.segmenta_por_puntos(tokens, elimina_separadores=elimina_separadores)
        # Como no hemos segmentado por blancos (segmentan palabras pero no frases), eliminamos los blancos
        # al inicio y fin de cada frase.
        # tokens = [token.strip() for token in tokens]
        # Ahora mismo, los separadores están puesto como tokens aparte.
        # Por defecto, se indica que cada separador se meta con la frase a la que le toca.
        if not elimina_separadores and adjunta_separadores:
            # Pegamos el separador a la frase anterior o siguiente según toque, y lo pegamos añadiéndolo al
            # unicode del texto, o creando listas (según exprese agrupa_separadores)
            return Tokenizer.adjunta_separadores(tokens, separadores_agrupados=agrupa_separadores,
                                                 segmentado_por_palabras=False)
        return tokens

    @staticmethod
    def segmenta_por_frases(texto, elimina_separadores=False, elimina_separadores_blancos=True,
                            incluye_parentesis=False, adjunta_separadores=True, agrupa_separadores=False):
        u"""Se toma un texto de entrada y se devuelve segmentado por frases como una lista de strings.

        Los separadores de frases se eliminan o no según el parámetro. Y en caso de no eliminarse, cabe la
        posibilidad de que se adjunten como parte (inicial o final) de una frase, o de que se dejen como
        tokens independientes al inicio o fin de una frase.

        Se considera que una frase la constituye una cadena de texto que termina en un punto "segmentador" o
        en alguno de los segmentadores no ambiguos (tabuladores o signos de exclamación, interrogación...).
        Por lo tanto, segmentar por frases equivalente a aplicar la segmentación no ambigua, y después la
        segmentación de puntos.

        :type texto: unicode
        :param texto: La cadena de caracteres que conforma el texto de entrada.
        :type elimina_separadores: bool
        :param elimina_separadores: Si está a True, los separadores se eliminan del resultado.
            Si está a False, dichos separadores se incluyen como tokens independientes en el listado final.
        :type elimina_separadores_blancos: bool
        :param elimina_separadores_blancos: Lo mismo que elimina_separadores pero en específico para los que
            son separadores blancos.
        :type incluye_parentesis: bool
        :param incluye_parentesis: Si está a True, también se usan los "paréntesis" ("()[]{}") para segmentar.
            Si está a False, dichos caracteres no segmentan nada.
        :type adjunta_separadores: bool
        :param adjunta_separadores: Si es False, los signos ortográficos se dan como tokens independientes.
            Si está a True los signos ortográficos no se colocan como tokens independientes sino que se
            adjuntan al siguiente/anterior token según corresponda: los signos de apertura se añaden al
            siguiente y los de cierre y pausa se adjuntan al anterior.
        :type agrupa_separadores: bool
        :param agrupa_separadores: Solo afecta si adjunta_separadores es True. En dicho caso,
            si este parámetro está a True, cada frase no es un simple unicode, sino que es una lista de
            unicodes: signos de apertura, texto y signos de cierre de frase. Si este parámetro está a
            False, entonces se devuelve un listado de unicodes, que pueden ser el texto de la frase o de
            los signos de apertura/cierre.
        :rtype: [unicode]
        :return: Una lista de cadenas de texto, cada una representando a una frase o a un separador.
        """
        if not texto:
            return []
        # Se prefiere el uso de los puntos suspensivos como un único carácter porque facilita el
        # procesado al consistir, como todos los demás signos de puntuación, en un único carácter.
        texto = texto.replace(u'...', u'…')
        # Primero segmentamos según caracteres que siempre dividen palabras (y frases).
        tokens = Tokenizer.segmenta_por_no_ambiguos([texto],
                                                    elimina_separadores=elimina_separadores,
                                                    elimina_separadores_blancos=elimina_separadores_blancos
                                                    if (elimina_separadores or not adjunta_separadores)
                                                    else False,
                                                    incluye_parentesis=incluye_parentesis)
        # Después por dos puntos.
        tokens = Tokenizer.segmenta_por_dos_puntos(tokens, elimina_separadores=elimina_separadores)
        # Después por puntos.
        tokens = Tokenizer.segmenta_por_puntos(tokens, elimina_separadores=elimina_separadores)
        # Como no hemos segmentado por blancos (segmentan palabras pero no frases), eliminamos los blancos
        # al inicio y fin de cada frase.
        # tokens = [token.strip() for token in tokens]
        # Ahora mismo, los separadores están puesto como tokens aparte.
        # Por defecto, se indica que cada separador se meta con la frase a la que le toca.
        if not elimina_separadores and adjunta_separadores:
            # Pegamos el separador a la frase anterior o siguiente según toque, y lo pegamos añadiéndolo al
            # unicode del texto, o creando listas (según exprese agrupa_separadores)
            return Tokenizer.adjunta_separadores(tokens, separadores_agrupados=agrupa_separadores,
                                                 segmentado_por_palabras=False,
                                                 elimina_separadores_blancos=elimina_separadores_blancos)
        return tokens

    @staticmethod
    def segmenta_por_palabras(tokens, elimina_separadores=False,
                              segmenta_por_guiones_internos=True, segmenta_por_guiones_externos=True,
                              segmenta_por_apostrofos_internos=False, segmenta_por_apostrofos_externos=True,
                              adjunta_separadores=False, agrupa_separadores=False):
        u"""Se toma una lista de frases y se devuelve una lista de palabras.

        Se toma un texto de entrada y se devuelve segmentado por palabra. El texto de entrada puede ser una
        cadena de texto (en cuyo caso se toma como una única frase) o una lista (formada por elementos que son
        str y que representa cada uno a una frase). Los separadores de frase (y por tanto también de palabra)
        y palabra no se quitan (salvo los blancos) y se pueden adjuntar a la palabra a la que corresponda (por
        defecto) o se se dejan como tokens independientes al inicio o fin de una palabra: por ejemplo, los
        cierres, comas, puntos... se asignarán a la palabra anterior (si es que no queremos tenerlos como
        tokens independientes); y los cierres se añaden a la palabra anterior.

        :type tokens: [unicode]
        :param tokens: Una lista de cadenas de caracteres, cada una de ellas representando a una frase.
        :type elimina_separadores: bool
        :param elimina_separadores: Si está a True, los separadores se eliminan del resultado. Si es False,
            dichos separadores se incluyen como tokens independientes en el listado final.
        :type segmenta_por_guiones_internos: bool
        :param segmenta_por_guiones_internos: Si está a True, se segmenta por guiones completamente
            rodeados de caracteres no blancos (lo cual separa cosas como "judeo-masónica").
        :type segmenta_por_guiones_externos: bool
        :param segmenta_por_guiones_externos: Si está a True, se segmenta por guiones no completamente
            rodeados de caracteres no blancos (lo cual separa el guion de un prefijo, pero también aquellos
            guiones que funcionan como si fueran paréntesis).
        :type segmenta_por_apostrofos_externos: bool
        :param segmenta_por_apostrofos_externos: Si está a True, se segmenta por apóstrofos/comillas simples
            no completamente rodeados de caracteres no blancos (cuando funciona como comilla).
        :type segmenta_por_apostrofos_internos: bool
        :param segmenta_por_apostrofos_internos: Si está a True, se segmenta por apóstrofos/comillas simples
            completamente rodeados de caracteres no blancos (cuando funciona como apóstrofo).
        :type adjunta_separadores: bool
        :param adjunta_separadores: Si es False, los separadores se devuelven como tokens independientes.
            Si es True los separadores no se colocan como tokens independientes sino que se adjuntan al
            siguiente/anterior token según corresponda: los signos de apertura se añaden al siguiente y los de
            cierre y pausa se adjuntan al anterior.
        :type agrupa_separadores: bool
        :param agrupa_separadores: Solo afecta si adjunta_separadores es True. En dicho caso,
            si este parámetro está a True, cada frase no es un simple unicode, sino que es una lista de
            unicodes: signos de apertura, texto y signos de cierre de frase. Si este parámetro está a
            False, entonces se devuelve un listado de unicodes, que pueden ser el texto de la frase o de
            los signos de apertura/cierre.
        :return: una list con los tokens (que son str)
        """
        # Primero segmentamos por comas siempre y cuando no estén dentro de una cadena de números.
        tokens = Tokenizer.segmenta_por_comas(tokens, elimina_separadores=elimina_separadores)
        # Lo mismo con las barras.
        tokens = Tokenizer.segmenta_por_barras(tokens, elimina_separadores=elimina_separadores)
        # Además, segmentamos por guiones.
        tokens = Tokenizer.segmenta_por_guiones(tokens, elimina_separadores=elimina_separadores,
                                                segmenta_por_guiones_internos=segmenta_por_guiones_internos,
                                                segmenta_por_guiones_externos=segmenta_por_guiones_externos)
        # También segmentamos por las comillas simples o apóstrofos.
        tokens = Tokenizer.\
            segmenta_por_apostrofos(tokens, elimina_separadores=elimina_separadores,
                                    segmenta_por_apostrofos_internos=segmenta_por_apostrofos_internos,
                                    segmenta_por_apostrofos_externos=segmenta_por_apostrofos_externos)
        # Y hacemos el segmentado múltiple final: paréntesis, otros signos de puntuación, especiales y blancos
        tokens = Tokenizer.segmenta_por_multiple(tokens, elimina_separadores=elimina_separadores,
                                                 elimina_separadores_blancos=True)
        # Ahora adjuntamos o no los segmentadores al token correspondiente.
        if adjunta_separadores and not elimina_separadores:
            # Pegamos el separador a la palabra anterior o siguiente según toque, y lo pegamos añadiéndolo al
            # unicode del texto, o creando listas (según exprese agrupa_separadores)
            return Tokenizer.adjunta_separadores(tokens, separadores_agrupados=agrupa_separadores,
                                                 segmentado_por_palabras=True)
        return tokens

    @staticmethod
    def adjunta_separadores(tokens, separadores_agrupados=False, segmentado_por_palabras=False,
                            elimina_separadores_blancos=False):
        u"""Fusiona (o agrupa en listas) los tokens separadores (de palabra/frase) con el token (no separador)
        al que corresponda.

        Al segmentar, los separadores (que no sean blancos) no siempre se eliminan, sino que según el valor
        de los parámetros, es posible que se adjunten como tokens (fusionados con el token de frase/palabra o
        bien agrupándolos en sublistas).
        Así u'¡Hola, Iván!' se segmentaría  como:
        - [u'¡', u'Hola, Iván', u'!'] (en un segmentado por frases).
        - [u'¡', u'Hola', u',', u'Iván', u'!'] (en un segmentado por palabras)
        Una vez realizado el segmentado, se nos pasan esas listas a este método, que adjuntará/agrupará las
        pausas a los tokens correspondientes y se devolverá respectivamente las listas:
        - [u'¡Hola, Iván!'] y [u'¡Hola,', u'Iván!'] (si decidimos adjuntar),
        - [[u'¡', u'Hola, Iván', u'!']] y [[u'¡', u'Hola', u',', u'Iván', u'!']] (si decidimos agrupar).

        :type tokens: [unicode]
        :param tokens: Una lista de tokens del segmentado previo que se haya realizado. Cada token de la lista
            puede ser una frase/palabra, o bien un carácter segmentador.
        :type separadores_agrupados: bool
        :param separadores_agrupados: Indica si el tokenizado previo se ha hecho adjuntando y agrupando los
            separadores, en cuyo caso los tokens no son una lista de unicodes sino una lista de listas de
            unicodes.
        :type segmentado_por_palabras: bool
        :param segmentado_por_palabras: Indica si el tokenizado son palabras de una frase con sus separadores,
            o si se trata de frases, con sus separadores. En el segundo caso, si los separadores no están
            agrupados, se unen los unicodes para dar lugar a la frase completa.
        :type elimina_separadores_blancos: bool
        :param elimina_separadores_blancos: Los separadores blancos (saltos de línea, tabuladores, etc.) se
            consideran "cierres duros", de forma que siempre marcan un punto de corte entre palabras y frases.
            Si este parámetro está a True, se respetan dichos cortes pero se eliminan los separadores. Si está
            a False, dichos separadores se adjuntan como final del token anterior.
        :rtype: [unicode]
        :return: La nueva lista de tokens en el que los separadores se han adjuntado al token previo/posterior
        """
        # Al agrupar separadores no se crea una lista de unicodes, sino una lista de listas de unicodes.
        # Por ello, para no estar en muchas líneas de código haciendo una cosa u otra según el valor del
        # parámetro, directamente se separa aquí en dos ramas de código, y así es más eficiente.
        tokens_con_pausas = []
        n_comillas_dobles = 0
        cierre_visto = False
        if separadores_agrupados:
            for orden_token, token in enumerate(tokens):
                if not tokens_con_pausas:
                    # Es el primero, lo añadimos sin más
                    tokens_con_pausas.append([token])
                    n_comillas_dobles += token.count(u'"')
                else:
                    # Pasamos los tokens de cierre al token anterior. Puede haber espacios que procesar, si al
                    # inicio hay un cierre, espacio y otro cierre, por ejemplo. Los espacios se borran.
                    while token and (token[0] in u' \t\n\r\f\v.:…;?!,)]}”»>’´\\/|"'):
                        if token[0] in u'\t\n\r\f\v':
                            # Es un cierre duro que corta completamente. Lo metemos directamente como final
                            # del token anterior.
                            cierre_visto = True
                            if not elimina_separadores_blancos:
                                tokens_con_pausas[-1] += [token[:1]]
                        elif token[0] in u'.:…;?!,)]}”»>’´\\/|' and\
                                tokens_con_pausas[-1][-1] not in u'\t\n\r\f\v':
                            # Es un cierre que debe ir con el token anterior ya que no había un cierre duro
                            # y permite agrupar varios signos ortográficos.
                            if token[0] in u'.:;?!':
                                cierre_visto = True
                            elif token[0] in u'…' and tokens_con_pausas[-1][-1][-1] not in u'([{':
                                if len(token) > 1 and token[1:].strip() and\
                                        token[1:].strip()[0] not in u')]}':
                                    cierre_visto = True
                                elif orden_token < len(tokens) - 1 and\
                                        tokens[orden_token + 1].strip() and\
                                        tokens[orden_token + 1].strip()[0] not in u')]}':
                                    cierre_visto = True
                            tokens_con_pausas[-1] += [token[:1]]
                        elif token[0] in u'"':
                            # Las comillas son muy peliagudas, ya que pueden ir antes o después de un punto,
                            # por ejemplo, y ser parte del mismo grupo de corte. Pondremos junto al anterior
                            # solo si hemos visto una cantidad impar de comillas desde el último cierre duro.
                            if n_comillas_dobles % 2:
                                # Esta es la comilla que cierra, así que va con el token anterior.
                                tokens_con_pausas[-1] += [token[:1]]
                                n_comillas_dobles += 1
                            elif cierre_visto:
                                # Es una comilla de apertura y ya se ha visto un cierre, así que al siguiente.
                                break
                            else:
                                n_comillas_dobles += 1
                        token = token[1:]  # Eliminamos el carácter procesado.
                    if token:
                        if tokens_con_pausas[-1][-1] in u'¿¡([{“«<‘`' or \
                                (tokens_con_pausas[-1][-1] in u'-‒–−­—―' and token[0] in u'0123456789¿¡([{<')\
                                or (tokens_con_pausas[-1][-1] == u'"' and n_comillas_dobles % 2):
                            # El token anterior era signo de apertura (o negativo), metemos la palabra con él.
                            tokens_con_pausas[-1] += [token]
                        else:
                            if token[0] in u'¿¡' or cierre_visto:
                                # Es una apertura dura o hemos visto el cierre y esto toca en el siguiente
                                # token. Crea un nuevo token ya que el anterior no es de apertura.
                                tokens_con_pausas.append([token])
                                cierre_visto = False
                            else:
                                # No hemos visto un cierre, así que lo metemos en token anterior
                                tokens_con_pausas[-1] += [token]
                        n_comillas_dobles += token.count(u'"')
        else:
            for orden_token, token in enumerate(tokens):
                if not tokens_con_pausas or tokens_con_pausas[-1][-1] in u'\t\n\r\f\v':
                    # Es el primero, o venimos de un salto de carro, tabulador, etc... lo añadimos sin más
                    if tokens_con_pausas and elimina_separadores_blancos:
                        tokens_con_pausas[-1] = tokens_con_pausas[-1].strip()
                    tokens_con_pausas.append(token)
                    n_comillas_dobles += token.count(u'"')
                else:
                    # Pasamos los tokens de cierre al token anterior. Puede haber espacios que procesar, si al
                    # inicio hay un cierre, espacio y otro cierre, por ejemplo "? ?". Los espacios se borran.
                    while token and (token[0] in u' \t\n\r\f\v.:…;?!,)]}”»>’´\\/|"'):
                        if token[0] in u'\t\n\r\f\v':
                            # Es un cierre duro que corta completamente. Lo metemos directamente como final
                            # del token anterior.
                            cierre_visto = True
                            tokens_con_pausas[-1] += token[:1]
                        elif token[0] in u'.:…;?!,)]}”»>’´\\/|':
                            # Es un cierre que debe ir con el token anterior ya que no había un
                            # cierre duro y permite agrupar varios signos ortográficos.
                            if token[0] in u'.:;?!':
                                cierre_visto = True
                            elif token[0] in u'…' and tokens_con_pausas[-1][-1] not in u'([{':
                                if len(token) > 1 and token[1:].strip() and\
                                        token[1:].strip()[0] not in u')]}':
                                    cierre_visto = True
                                elif orden_token < len(tokens) - 1 and\
                                        tokens[orden_token + 1].strip() and\
                                        tokens[orden_token + 1].strip()[0] not in u')]}':
                                    cierre_visto = True
                            tokens_con_pausas[-1] += token[:1]
                        elif token[0] in u'"':
                            # Las comillas son muy peliagudas, ya que pueden ir antes o después de un punto,
                            # por ejemplo, y ser parte del mismo grupo de corte. Pondremos junto al anterior
                            # solo si hemos visto una cantidad impar de comillas desde el último cierre duro.
                            if n_comillas_dobles % 2:
                                # Esta es la comilla que cierra, así que va con el token anterior.
                                tokens_con_pausas[-1] = tokens_con_pausas[-1].strip() + token[:1]
                                n_comillas_dobles += 1
                            elif cierre_visto:
                                # Es una comilla de apertura y ya se ha visto un cierre, así que al siguiente.
                                break
                            else:
                                n_comillas_dobles += 1
                        else:
                            # Es un espacio, y como tenemos strings, lo pasamos al último token.
                            tokens_con_pausas[-1] += token[:1]
                        token = token[1:]  # Eliminamos el carácter procesado.
                    if token:
                        token_strip = tokens_con_pausas[-1].strip()
                        if token_strip[-1] in u'¿¡([{“«<‘`' or \
                                (token_strip[-1] in u'-‒–−­—―' and token[0] in u'0123456789¿¡([{<') or\
                                (token_strip[-1] in u'"' and n_comillas_dobles % 2):
                            # El token anterior era signo de apertura (o negativo), metemos la palabra con él.
                            tokens_con_pausas[-1] += token
                        else:
                            if segmentado_por_palabras:
                                tokens_con_pausas[-1] = tokens_con_pausas[-1].strip()
                                tokens_con_pausas.append(token)
                                cierre_visto = False
                            else:
                                if token[0] in u'¿¡' or cierre_visto:
                                    # Es una apertura dura o hemos visto el cierre y esto toca en el siguiente
                                    # token. Crea un nuevo token ya que el anterior no es de apertura.
                                    tokens_con_pausas[-1] = tokens_con_pausas[-1].strip()
                                    tokens_con_pausas.append(token)
                                    cierre_visto = False
                                else:
                                    # No hemos visto un cierre, así que lo metemos en el token anterior
                                    tokens_con_pausas[-1] += token

                        n_comillas_dobles += token.count(u'"')
        return tokens_con_pausas

    @staticmethod
    def segmenta_por_no_ambiguos(tokens, elimina_separadores=False, elimina_separadores_blancos=True,
                                 incluye_parentesis=True):
        u"""Segmenta los elementos de una lista de tokens por caracteres que siempre segmentan frases
        (y palabras)

        Este método toma una lista de tokens y los devuelve segmentados según los signos de puntuación no
        ambiguos, así como blancos que no sean simples espacios (es decir, tabuladores, saltos de línea...).

        Los caracteres de paréntesis (incluyendo corchetes y llaves) se consideran o no como segmentadores
        según el parámetro. Además, El espacio blanco no se considera que segmente tokens (en este
        segmentado), y se utilizará (o no) como carácter segmentador en otro método.

        Los separadores (caracter(es) que segmenta(n)) se devuelven o no en la lista final segmentada según
        los parámetros. Los caracteres blancos tienen un tratamiento algo especial, con su propio parámetro,
        que indica si se incluyen o no. Además, según el parámetro se eliminan también los blancos que queden
        en los extremos (si se opta por no eliminar los blancos, esto solo afecta a los espacios).

        Al segmentar una [unicode] se devuelve otra [unicode] con más elementos que la lista inicial (salvo
        que ningún token de la lista original incluya ningún carácter segmentador).

        :type tokens: [unicode]
        :param tokens: Una lista con los tokens del segmentado previo que se haya realizado. Cada token de
            esa lista puede ser una frase/palabra, o bien un carácter segmentador.
        :type elimina_separadores: bool
        :param elimina_separadores: Si está a True, los separadores se eliminan del resultado.
            Si está a False, dichos separadores se incluyen como tokens independientes en el listado final.
        :type elimina_separadores_blancos: bool
        :param elimina_separadores_blancos: Lo mismo que elimina_separadores pero en específico para los que
            son separadores blancos.
        :type incluye_parentesis: bool
        :param incluye_parentesis: Si está a True, también se usan los "paréntesis" ("()[]{}") para el
            segmentado. Si está a False, dichos caracteres no segmentan nada.
        :rtype: [unicode]
        :return: Una lista con los tokens (que son cadenas de caracteres) que resultan tras segmentar.
        """
        # TODO: Debe de haber algún tipo de bug, pero si pongo el regexp como un string r'', no funciona lo
        #   de segmentar por puntos suspensivos.
        parentesis = u'()\[\]{}' if incluye_parentesis else u''
        blancos = u'' if elimina_separadores_blancos else u'\t\n\r\f\v'
        regex = u'(?:[^¿?¡!;…\t\n\r\f\v' + parentesis + u']+)' +\
            (u'' if elimina_separadores else u'|(?:[¿?¡!;…' + blancos + parentesis + u'])')
        segmentador = RegexpTokenizer(regex)
        return [token.strip(u' ')
                for token_inicial in tokens
                for token in segmentador.tokenize(token_inicial)
                if token.strip(u' ')]

    @staticmethod
    def segmenta_por_dos_puntos(tokens, elimina_separadores=False):
        u"""Se segmenta la lista de tokens por el signo u':' cuando no sea parte de un número (quizá hora).

        Los separadores (caracter(es) que segmenta(n)) se devuelven o no en la lista final segmentada según el
        parámetro.

        Al segmentar una [unicode] se devuelve otra [unicode] con más elementos que la lista inicial (salvo
        que ningún token de la lista original incluya ningún carácter segmentador).

        :type tokens: [unicode]
        :param tokens: Una [str] con los tokens del segmentado previo que se haya realizado. Cada token de
            esa lista puede ser una frase/palabra, o bien un carácter segmentador.
        :type elimina_separadores: bool
        :param elimina_separadores: Si está a True, los separadores se eliminan del resultado.
            Si está a False, dichos separadores se incluyen como tokens independientes en el listado final.
        :rtype: [unicode]
        :return: una list con los tokens (que son str) que resultan tras segmentar.
        """
        regex = r'(?:[^:]+(?:(?<=\d):(?=\d)[^:]+)*)' + (r'' if elimina_separadores else r'|:')
        segmentador = RegexpTokenizer(regex)
        return [token for token_inicial in tokens for token in segmentador.tokenize(token_inicial)]

    @staticmethod
    def segmenta_por_puntos(tokens, elimina_separadores=False):
        u"""Se segmenta la lista de tokens por el signo u'.' cuando no sea parte de un número

        Este método toma una lista de tokens y los devuelve segmentados por puntos siempre que no formen parte
        de un número, de un acrónimo o de una abreviatura. También separa por puntos suspensivos.
        El segmentado por u'.' es el más complejo, ya que es ambiguo. En concreto, evitamos partir por puntos
        cuando:
            - Forma parte de un número (es decir, el punto está precedido y seguido de un número).
              Para asegurarnos, usaremos un lookahead como con las comas.
            - Está incluido en una sigla. Las siglas son una o dos letras mayúsculas iguales al inicio de
            palabra, seguidas de un punto. Necesitamos un lookbehind.
            - El punto forma parte de una abreviatura (es decir, el punto va precedido por alguno de los
              textos de nuestra lista de abreviaturas, a su vez precedido de inicio de palabra).
        Python tiene una limitación muy importante con los lookbehind: tienen que tener una longitud fija de
        caracteres. Así que no podemos usar los metacaracteres de repetición y en general estamos un poco
        maniatados, de ahí que la expresión regular parezca que pudiera agruparse mejor, pero no es así,
        porque hay algunos caracteres como \b que no avanzan el cursor.
        Puesto que la expresión regular es algo compleja, se explica a continuación:
        (
            # Vamos leyendo mientras no encontremos un punto.
            [^.]+
            (
                # Antes de meter el punto como parte del token, comprobamos...
                (
                    # Que sea un punto rodeado de números, o
                    ((?<=\d)(?=\.\d))
                    |
                    # Que el punto sea parte de una sigla (letras mayúsculas sin tilde separadas por puntos),
                    # es decir:
                    (
                        # Que el punto esté precedido de una mayúscula que inicia
                        # palabra (inicio de acrónimo), o
                        (?<=\b[A-ZÑ])
                        |
                        # Igual que el anterior para acrónimos de plurales tipo EE.UU., o
                        (?<=\b[A-ZÑ]{2,2})
                        |
                        # Que esté precedido de una mayúscula precedida de punto
                        # (en mitad de acrónimo), o
                        (?<=(\.|\W)[A-ZÑ])
                        |
                        # Igual que el anterior para acrónimos de plurales tipo EE.UU., o
                        (?<=(\.|\W)[A-ZÑ]{2,2})
                    )
                )
                # Si hemos pasado el examen anterior, incluimos el punto en el token.
                \.
                # Tras el punto, puede venir uno o más "no puntos"
                [^.]*
            )*
        )
        |
        # En cualquier otro caso, tomamos el punto, o los puntos suspensivos, como token.
        (\.(\.\.)?)

        Los separadores (caracter(es) que segmenta(n)) se devuelven o no en la lista final segmentada según el
        parámetro.

        Al segmentar una [unicode] se devuelve otra [unicode] con más elementos que la lista inicial (salvo
        que ningún token de la lista original incluya ningún carácter segmentador).

        :type tokens: [unicode]
        :param tokens: Una [str] con los tokens del segmentado previo que se haya realizado. Cada token de
            esa lista puede ser una frase/palabra, o bien un carácter segmentador.
        :type elimina_separadores: bool
        :param elimina_separadores: Si está a True, los separadores se eliminan del resultado.
            Si está a False, dichos separadores se incluyen como tokens independientes en el listado final.
        :rtype: [unicode]
        :return: una list con los tokens (que son str) que resultan tras segmentar.
        """
        regex = r'(?:[^.]+(?:(?:(?:(?<=\d)(?=\.\d))|(?:(?<=\b[A-ZÑ])|(?<=\b[A-ZÑ]{2,2})|' +\
            r'(?<=(?:\.|\W)[A-ZÑ])|(?<=(?:\.|\W)[A-ZÑ]{2,2})))' +\
            r'\.' +\
            r'[^.]*)*)' + (r'' if elimina_separadores else r'|(?:\.(?:\.\.)?)')
        segmentador = RegexpTokenizer(regex)
        return [token for token_inicial in tokens for token in segmentador.tokenize(token_inicial)]

    @staticmethod
    def segmenta_por_blancos(tokens, elimina_separadores=False, elimina_separadores_blancos=True):
        u"""Este método toma una lista de tokens y los devuelve segmentados por caracteres blancos.

        Los blancos pueden ser cualquiera, desde espacio a tabuladores, saltos de línea...

        Los separadores (caracter(es) que segmenta(n)) se devuelven o no en la lista final segmentada según el
        parámetro.

        Al segmentar una [unicode] se devuelve otra [unicode] con más elementos que la lista inicial (salvo
        que ningún token de la lista original incluya ningún carácter segmentador).

        :type tokens: [unicode]
        :param tokens: Una [unicode] con los tokens del segmentado previo que se haya realizado. Cada token
            de esa lista puede ser una frase/palabra, o bien un carácter segmentador.
        :type elimina_separadores: bool
        :param elimina_separadores: Si está a True, los separadores se eliminan del resultado. Si está a
            False, dichos separadores se incluyen como tokens independientes en el listado final.
        :type elimina_separadores_blancos: bool
        :param elimina_separadores_blancos: Si está a False, los blancos segmentadores se incluyen como
            tokens apartes (excepto por el espacio). Si está a True, todos los blancos segmentadores se
            eliminan y no aparecen en el listado de tokens.
        :rtype: [unicode]
        :return: una list con los tokens (que son unicode) que resultan tras segmentar.
        """
        blancos = r'' if elimina_separadores_blancos else r'\t\n\r\f\v'
        regex = r'(?:[^\s]+)' + (r'' if elimina_separadores else (r'|(?:[' + blancos + r']+)'))
        segmentador = RegexpTokenizer(regex)
        return [token for token_inicial in tokens for token in segmentador.tokenize(token_inicial)]

    @staticmethod
    def segmenta_por_comas(tokens, elimina_separadores=False):
        u"""Toma una lista de tokens y los segmenta por el signo u',' siempre que no forme parte de un número.

        Los separadores (caracter(es) que segmenta(n)) se devuelven o no en la lista final segmentada según el
        parámetro.

        Al segmentar una [unicode] se devuelve otra [unicode] con más elementos que la lista inicial (salvo
        que ningún token de la lista original incluya ningún carácter segmentador).

        :type tokens: [unicode]
        :param tokens: Una [str] con los tokens del segmentado previo que se haya realizado. Cada token de
            esa lista puede ser una frase/palabra, o bien un carácter segmentador.
        :type elimina_separadores: bool
        :param elimina_separadores: Si está a True, los separadores se eliminan del resultado.
            Si está a False, dichos separadores se incluyen como tokens independientes en el listado final.
        :rtype: [unicode]
        :return: una list con los tokens (que son str) que resultan tras segmentar.
        """
        regex = r'(?:[^,]+(?:(?<=\d),(?=\d)[^,]+)*)' + (r'' if elimina_separadores else r'|,')
        segmentador = RegexpTokenizer(regex)
        return [token for token_inicial in tokens for token in segmentador.tokenize(token_inicial)]

    @staticmethod
    def segmenta_por_barras(tokens, elimina_separadores=False):
        u"""Toma una lista de tokens y los segmenta por caracteres de barras si no forme parte de un número.

        Este método toma una lista de tokens y los devuelve segmentados por las barras u'\', u'/', u'|',
        siempre y cuando dicho signo no forme parte de un número (quizá una fecha).

        Los separadores (caracter(es) que segmenta(n)) se devuelven o no en la lista final segmentada según el
        parámetro.

        Al segmentar una [unicode] se devuelve otra [unicode] con más elementos que la lista inicial (salvo
        que ningún token de la lista original incluya ningún carácter segmentador).

        :type tokens: [unicode]
        :param tokens: Una [str] con los tokens del segmentado previo que se haya realizado. Cada token de
            esa lista puede ser una frase/palabra, o bien un carácter segmentador.
        :type elimina_separadores: bool
        :param elimina_separadores: Si está a True, los separadores se eliminan del resultado.
            Si está a False, dichos separadores se incluyen como tokens independientes en el listado final.
        :rtype: [unicode]
        :return: una list con los tokens (que son str) que resultan tras segmentar.
        """
        regex = r'(?:[^\\/|]+(?:(?<=\d)[\\/](?=\d)[^\\/|]+)*)' + (r'' if elimina_separadores else r'|[\\/|]')
        segmentador = RegexpTokenizer(regex)
        return [token for token_inicial in tokens for token in segmentador.tokenize(token_inicial)]

    @staticmethod
    def segmenta_por_guiones(tokens, elimina_separadores=False, segmenta_por_guiones_internos=True,
                             segmenta_por_guiones_externos=True):
        u"""Este método toma una lista de tokens y los devuelve segmentados según los guiones.

        Los separadores (caracter(es) que segmenta(n)) se devuelven o no en la lista final segmentada según el
        parámetro.

        Al segmentar una [unicode] se devuelve otra [unicode] con más elementos que la lista inicial (salvo
        que ningún token de la lista original incluya ningún carácter segmentador, o se eliminen).

        :type tokens: [unicode]
        :param tokens: Una [str] con los tokens del segmentado previo que se haya realizado. Cada token de esa
            lista puede ser una frase/palabra, o bien un carácter segmentador.
        :type elimina_separadores: bool
        :param elimina_separadores: Si está a True, los separadores se eliminan del resultado.
            Si está a False, dichos separadores se incluyen como tokens independientes en el listado final.
        :type segmenta_por_guiones_internos: bool
        :param segmenta_por_guiones_internos: Si está a True, se segmenta por guiones completamente
            rodeados de caracteres no blancos (lo cual separa cosas como "judeo-masónica").
        :type segmenta_por_guiones_externos: bool
        :param segmenta_por_guiones_externos: Si está a True, se segmenta por guiones no completamente
            rodeados de caracteres no blancos (lo cual separa el guion de un prefijo, pero también aquellos
            guiones que funcionan como si fueran paréntesis).
        :rtype: [unicode]
        :return: una list con los tokens (que son str) que resultan tras segmentar.
        """
        # TODO: Debe de haber algún tipo de bug, pero si pongo el regexp como un string r'', no funciona lo
        #   de segmentar por algunos caracteres "raros".
        if segmenta_por_guiones_internos and segmenta_por_guiones_externos:
            regex = u'(?:(?:[-‒–−­—―]\d)?(?:[^-‒–−­—―]+))+' +\
                    (u'' if elimina_separadores else u'|(?:[-‒–−­—―])')
        elif segmenta_por_guiones_internos:
            regex = u'(?:(?:(?:[^-‒–−­—―]+)(?:(?:(?<=\W)[-‒–−­—―])|(?:[-‒–−­—―](?=\W)))?)+)' +\
                    (u'' if elimina_separadores else u'|(?<=\w)[-‒–−­—―](?=\w)')
        elif segmenta_por_guiones_externos:
            regex = u'(?:(?:(?:(?:[-‒–−­—―]\d)?(?:[^-‒–−­—―]+))+(?:(?:(?<=\w)[-‒–−­—―](?=\w)))?)+)' + \
                    (u'' if elimina_separadores else
                     u'|(?:(?:(?<=\W)[-‒–−­—―])|(?:(?<=^)[-‒–−­—―])|(?:[-‒–−­—―](?=\W))|(?:[-‒–−­—―](?=$)))')
        else:
            # No es normal que se pida segmentar por guiones pero que no sean ni internos ni externos.
            return tokens
        segmentador = RegexpTokenizer(regex)
        return [token for token_inicial in tokens for token in segmentador.tokenize(token_inicial)]

    @staticmethod
    def segmenta_por_apostrofos(tokens, elimina_separadores=False, segmenta_por_apostrofos_internos=False,
                                segmenta_por_apostrofos_externos=True):
        u"""Este método toma una lista de tokens y los devuelve segmentados según las comillas/apóstrofos.

        Son caracteres que también pueden usarse como comilla simple, y por lo tanto pueden considerarse como
        separadores cuando van o no rodeados de caracteres alfabéticos a su alrededor.

        Al segmentar una [unicode] se devuelve otra [unicode] con más elementos que la lista inicial (salvo
        que ningún token de la lista original incluya ningún carácter segmentador, o se eliminen).

        :type tokens: [unicode]
        :param tokens: Una [str] con los tokens del segmentado previo que se haya realizado. Cada token de esa
            lista puede ser una frase/palabra, o bien un carácter segmentador.
        :type elimina_separadores: bool
        :param elimina_separadores: Si está a True, los separadores se eliminan del resultado.
            Si está a False, dichos separadores se incluyen como tokens independientes en el listado final.
        :type segmenta_por_apostrofos_internos: bool
        :param segmenta_por_apostrofos_internos: Si está a True, se segmenta por guiones completamente
            rodeados de caracteres no blancos (lo cual separa cosas como "judeo-masónica").
        :type segmenta_por_apostrofos_externos: bool
        :param segmenta_por_apostrofos_externos: Si está a True, se segmenta por guiones no completamente
            rodeados de caracteres no blancos (lo cual separa el guion de un prefijo, pero también aquellos
            guiones que funcionan como si fueran paréntesis).
        :rtype: [unicode]
        :return: una list con los tokens (que son str) que resultan tras segmentar.
        """
        # TODO: Debe de haber algún tipo de bug, pero si pongo el regexp como un string r'', no funciona lo
        #   de segmentar por algunos caracteres "raros".
        if segmenta_por_apostrofos_internos and segmenta_por_apostrofos_externos:
            regex = u'(?:[^\'‘`’´•·]+)' + (u'' if elimina_separadores else u'|(?:[\'‘`’´•·])')
        elif segmenta_por_apostrofos_internos:
            regex = u'(?:(?:(?:[^\'‘`’´•·]+)(?:(?:(?<=\W)[\'‘`’´•·])|(?:[\'‘`’´•·](?=\W)))?)+)' +\
                    (u'' if elimina_separadores else u'|(?<=\w)[\'‘`’´•·](?=\w)')
        elif segmenta_por_apostrofos_externos:
            regex = u'(?:(?:(?:[^\'‘`’´•·]+)(?:(?:(?<=\w)[\'‘`’´•·](?=\w)))?)+)' +\
                    (u'' if elimina_separadores else u'|(?:(?:(?<=\W)[\'‘`’´•·])|(?:(?<=^)[\'‘`’´•·])'
                                                     u'|(?:[\'‘`’´•·](?=\W))|(?:[\'‘`’´•·](?=$)))')
        else:
            # No es normal que se pida segmentar por apóstrofos pero que no sean ni internos ni externos.
            return tokens
        segmentador = RegexpTokenizer(regex)
        return [token for token_inicial in tokens for token in segmentador.tokenize(token_inicial)]

    @staticmethod
    def segmenta_por_multiple(tokens, elimina_separadores=False, elimina_separadores_blancos=True):
        u"""Este método toma una lista de tokens y los devuelve segmentados según una serie de caracteres:
        paréntesis, especiales y blancos.

        Es lo mismo que aplicar estos tres segmentados de forma sucesiva, pero más eficiente al hacer una
        única búsqueda.

        Los separadores (caracter(es) que segmenta(n)) se devuelven o no en la lista final segmentada según el
        parámetro. Además, se pueden dejar los guiones pero no el resto de blancos.

        Al segmentar una [unicode] se devuelve otra [unicode] con más elementos que la lista inicial (salvo
        que ningún token de la lista original incluya ningún carácter segmentador).

        :type tokens: [unicode]
        :param tokens: Una [unicode] con los tokens del segmentado previo que se haya realizado. Cada token de
            esa lista puede ser una frase/palabra, o bien un carácter segmentador.
        :type elimina_separadores: bool
        :param elimina_separadores: Si está a True, los separadores se eliminan del resultado. Si está a
            False, dichos separadores se incluyen como tokens independientes en el listado final.
        :type elimina_separadores_blancos: bool
        :param elimina_separadores_blancos: Si está a False, los blancos segmentadores se incluyen como tokens
            aparte (excepto por el espacio). Si está a True, todos los blancos segmentadores se eliminan y no
            aparecen en el listado de tokens
        :rtype: [unicode]
        :return: una list con los tokens (que son unicode) que resultan tras segmentar.
        """
        # TODO: Debe de haber algún tipo de bug, pero si pongo el regexp como un string r'', no funciona lo
        #   de segmentar por algunos caracteres "raros".
        blancos = u'' if elimina_separadores_blancos else u'\t\n\r\f\v'
        regex = u'(?:[^\s"“«”»<>@%&#()\[\]{}ªº°]+)' +\
                (u'' if elimina_separadores else (u'|(?:[' + blancos + u'"“«”»<>@%&#()\[\]{}ªº°])'))
        segmentador = RegexpTokenizer(regex)
        return [token for token_inicial in tokens for token in segmentador.tokenize(token_inicial)]

    @staticmethod
    def segmenta(texto, separa_frases=False):
        u"""Este es un método auxiliar, que hace los dos segmentados más típicos: por tokens, agrupándolos
        o no por frases.

        :type texto: unicode
        :param texto: Es el texto de entrada. Debe ser una cadena de texto, a ser posible en modo unicode.
        :type separa_frases: bool
        :param separa_frases: Si está a False, se devuelve una lista con todos los tokens del texto.
            Si está a True, se devuelve una lista de listas de tokens, donde cada elemento de la lista
            principal es una lista de tokens de una frase.
        :rtype: [unicode]
        :return: Una lista de tokens (si separa_frases es False) o una lista de (frases) de listas de tokens.
        """
        frases = Tokenizer.segmenta_por_frases(texto,
                                               elimina_separadores=False,
                                               elimina_separadores_blancos=True,
                                               incluye_parentesis=False,
                                               adjunta_separadores=True,
                                               agrupa_separadores=True)
        if separa_frases:
            # Así se crea una lista donde cada elemento representa una frase como una lista de tokens.
            return [Tokenizer.segmenta_por_palabras(frase_tokens,
                                                    elimina_separadores=False,
                                                    segmenta_por_guiones_internos=False,
                                                    segmenta_por_guiones_externos=True,
                                                    adjunta_separadores=False,
                                                    agrupa_separadores=False)
                    for frase_tokens in frases]
        else:
            # Así se crea una lista donde cada elemento representa un token como un string.
            return Tokenizer.segmenta_por_palabras(
                    [string for frase in frases for string in frase],
                    elimina_separadores=False,
                    segmenta_por_guiones_internos=False,
                    segmenta_por_guiones_externos=True,
                    adjunta_separadores=False,
                    agrupa_separadores=False)

    @staticmethod
    def segmenta_frases(texto):
        u"""Este es un método auxiliar, que segmenta un texto en frases y las devuelve como strings.

        :type texto: unicode
        :param texto: Es el texto de entrada. Debe ser una cadena de texto, a ser posible en modo unicode.
        :rtype: [unicode]
        :return: Una lista de frases como strings unicode.
        """
        # Así se crea una lista donde cada elemento representa una frase como un string.
        return Tokenizer.segmenta_por_frases(texto,
                                             elimina_separadores=False,
                                             elimina_separadores_blancos=True,
                                             incluye_parentesis=False,
                                             adjunta_separadores=True,
                                             agrupa_separadores=False)

    @staticmethod
    def test():
        u"""Este es un método que simplemente realiza un test, segmentando un texto en frases y tokens.
        """
        texto_prueba = u'Sol-luna es índico-Ártico, pero mató-asesinó a un caló-árabe (\'haber\').' \
                       u'Jorge d\'Alexandro dijo \'no\' a Barcelona\'92 al quedar 10º por Ü\'phone.' \
                       u'"Todo (…) duele." ' \
                       u'Es la verdad… ' \
                       u'Pero… ' \
                       u'no \'se sabe\'. ' \
                       u'Pero O\'Donnell nos dijo: ' \
                       u'"¿no es verdad…?" ' \
                       u'"¿Dime tú?"' \
                       u'Y nosotros no.\n' \
                       u'"Quedará París y el marxismo-leninismo (-raro-) -aunque no lo creas- a -2,3 grados".' \
                       u'" Todo ( … ) duele . " ' \
                       u'Es la verdad … ' \
                       u'Pero … ' \
                       u'no \' se sabe \'. ' \
                       u'Pero O\'Donnell nos dijo : ' \
                       u'" ¿ no es verdad … ? " ' \
                       u'" ¿ Dime tú ? " ' \
                       u'Y nosotros no . \n ' \
                       u'" Siempre quedará París y el marxismo-leninismo - aunque no lo creas - " . ' \
                       u'El 24/12 a las 23:59:59 es Navidad: cuando La Biblia dice que nació Chechu/Dios. ' \
                       u'45,23 es igual que 45.23 pero,45,23 es español:17 C.C.A.A. 17.'
        # Así se crea una lista donde cada elemento representa una palabra como un string.
        tokens_string = Tokenizer.segmenta(texto_prueba)
        # Así se crea una lista donde cada elemento representa una frase como una lista de tokens.
        tokens_frases = Tokenizer.segmenta(texto_prueba, separa_frases=True)
        # Así se crea una lista donde cada elemento representa una frase como un string.
        frases_string = Tokenizer.segmenta_frases(texto_prueba)
        for orden_frase, frase_string in enumerate(frases_string):
            print(u'Texto de frase ({:} tokens): {:}'.format(len(tokens_frases[orden_frase]), frase_string))
            print(u'\n'.join([u'\t{:2}: {}'.format(orden_token, token)
                              for orden_token, token in enumerate(tokens_frases[orden_frase])]) + u'\n')


if __name__ == "__main__":
    Tokenizer.test()
