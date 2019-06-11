from unicodedata import normalize


def norm_unicode(palabra):
    return normalize('NFKD', palabra)


def norm_utf8(palabra):
    return normalize('NFKC', palabra)


def babosear(palabra):
    # unicode de la 'a' a la 'z'
    conjunto_valido = {i for i in range(97, 123)}.union(
        {i for i in range(48, 57)})
    conjunto_valido.add(ord('_'))
    palabra = palabra.lower().replace(' ', '_')
    lista_valida = [x for x in palabra]
    palabra_valida = ''.join(lista_valida)
    palabra_unicode = norm_unicode(palabra_valida)
    valores_descartes = [771, 776, 769]
    lista_unicode = list(map(ord, palabra_unicode))
    # print(lista_unicode)
    lista_limpia = [
        x for x in lista_unicode if x not in valores_descartes and x in conjunto_valido]
    # print(lista_limpia)
    palabra_limpia = ''.join(map(chr, lista_limpia))
    palabra_utf8 = norm_utf8(palabra_limpia)
    return palabra_utf8


# para ejecutar en terminal python3 y despues:
#from herramientas.babosa import babosear
# cada vez que se guarda un cambio se reinicia la shell de python con Ctrl D
