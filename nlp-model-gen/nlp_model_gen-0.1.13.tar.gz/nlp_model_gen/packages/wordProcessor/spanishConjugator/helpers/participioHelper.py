# Recibe un verbo y devuelve su participio (se agrega participio en femenino
# y una variante más).
# <verb> verbo a conjugar debe ser una cadena de caracteres terminada en
# uno de {ar, er, ir, ár, ér, ír}. De no ser asi devuelve un vector vacio.
# <force_conj>: valor booleano. Si es verdadero fuerza a que el verbo
# sea conjugado por la función sin recurrir al diccionario de irregulares
# (aún si el mismo se encontrase allí)

# @Vendors
import fnmatch

def participio(verb, force_conj, mode, configs):
    irregular_verb_exceptions = configs['irregular_verb_exceptions'] 
    if not any(fnmatch.fnmatch(verb, suffix) for suffix in ['*ar', '*er', '*ir', '*ár', '*ér', '*ír']):
        return ['','','']
    verb_conj = []
    suffix_conj = []
    base_verb = verb[0:len(verb)-2]
    if not verb in irregular_verb_exceptions.keys() or force_conj:
        if fnmatch.fnmatch(verb, '*ar') or fnmatch.fnmatch(verb, '*ár'):
            suffix_conj = ['ado', 'ada', 'arse']
        if fnmatch.fnmatch(verb, '*er',) or fnmatch.fnmatch(verb, '*ér'):
            suffix_conj = ['ido', 'ida', 'erse']
        if fnmatch.fnmatch(verb, '*ir') or fnmatch.fnmatch(verb, '*ír'):
            suffix_conj = ['ido', 'ida', 'irse']
    else:
        return irregular_verb_exceptions[verb]['part']
    for suffix in suffix_conj:
        verb_conj.append(base_verb + suffix)

    #Verfica que el verbo no se encuentre en las excepciones del participio.
    #Verbos terminados con "olver", tienen su participio terminado con "uelto"
    if fnmatch.fnmatch(verb, '*olver'):
        verb_conj[0] = verb[0:len(verb)-5] + "uelto"
        verb_conj[1] = verb[0:len(verb)-5] + "uelta"

    # Cambio para los verbos terminados en 'decir'
    # iendo --> icho
    if fnmatch.fnmatch(verb, '*decir'):
        verb_conj[0] = verb[0:len(verb)-4] + "icho"
        verb_conj[1] = verb[0:len(verb)-4] + "icha"

    # Cambio para los verbos terminados en 'hacer'
    # iendo --> echo
    if fnmatch.fnmatch(verb, '*hacer'):
        verb_conj[0] = verb[0:len(verb)-4] + "echo"
        verb_conj[1] = verb[0:len(verb)-4] + "echa"

    # Cambio para 'pudir'
    # pudrido --> podrido
    if fnmatch.fnmatch(verb, '*pudrir'):
        verb_conj[0] = verb_conj[0].replace('u', 'o', 1)
        verb_conj[1] = verb_conj[1].replace('u', 'o', 1)

    return verb_conj
