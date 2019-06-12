# coding: utf-8
"""Módulo para funciones de lectura y escritura."""
from pathlib import Path

import pandas as pd

from banrep.preprocesos import filtrar_cortas
from banrep.utils import iterar_rutas


def leer_texto(archivo):
    """Lee texto de un archivo.

    Parameters
    ----------
    archivo : str | Path
        Ruta del archivo del cual se quiere leer texto.

    Returns
    -------
    str
       Texto de archivo.
    """
    ruta = Path(archivo).resolve()
    nombre = ruta.name
    carpeta = ruta.parent.name

    try:
        with open(ruta, encoding="utf-8") as f:
            texto = f.read()

    except OSError:
        print(f"No puede abrirse archivo {nombre} en {carpeta}.")
        texto = ""
    except UnicodeDecodeError:
        print(f"No puede leerse archivo {nombre} en {carpeta}.")
        texto = ""
    except Exception:
        print(f"Error inesperado leyendo {nombre} en {carpeta}")
        texto = ""

    return texto


def guardar_texto(texto, archivo):
    """Guarda texto en un archivo.

    Parameters
    -------------
    texto : str
        Texto que se quiere guardar.
    archivo : str | Path
        Ruta del archivo en el cual se quiere guardar texto.

    Returns
    ---------
    None
    """
    with open(archivo, "w", newline="\n", encoding="utf-8") as ruta:
        for fila in texto.splitlines():
            ruta.write(fila)
            ruta.write("\n")


def iterar_registros(directorio, aleatorio=False, chars=0, parrafos=False):
    """Itera rutas en directorio y extrae detalles de cada documento.

    Documento puede ser el texto de un archivo o cada párrafo en él.

    Parameters
    ----------
    directorio : str | Path
        Directorio a iterar.
    aleatorio : bool
        Iterar aleatoriamente.
    chars : int
        Mínimo número de caracteres en una línea de texto.
    parrafos : bool
        Considerar cada párrafo como documento.

    Yields
    ------
    tuple (str, dict)
        Información de cada documento (texto, metadata).
    """
    doc_id = 1
    for archivo in iterar_rutas(directorio, aleatorio=aleatorio):
        texto = leer_texto(archivo)
        if texto:
            if chars:
                texto = filtrar_cortas(texto, chars=chars)

            comun = {"archivo": archivo.name, "fuente": archivo.parent.name}

            if parrafos:
                for p in texto.splitlines():
                    if p:
                        info = {"doc_id": f"{doc_id:0>6}", **comun}
                        doc_id += 1
                        yield p, info

            else:
                info = {"doc_id": f"{doc_id:0>6}", **comun}
                doc_id += 1
                yield texto, info


def leer_palabras(archivo, hoja, col_grupo="type", col_palabras="word"):
    """Extrae grupos de palabras de un archivo Excel.

    Agrupa `col_palabras` por columna `col_grupo` de hoja `hoja` de archivo Excel.

    Parameters
    ----------
    archivo : str | Path
    hoja : str
    col_grupo : str
    col_palabras : str

    Returns
    -------
    dict (str:set)
       Grupos de palabras en cada grupo.
    """
    df = pd.read_excel(archivo, sheet_name=hoja)
    grupos = {k: set(v) for k, v in df.groupby(col_grupo)[col_palabras]}

    return grupos


def df_crear_textos(df, col_id, col_texto, directorio):
    """Crea archivo de texto en directorio para cada record de dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        En alguna de sus columnas tiene texto en cada fila.
    col_id : str
        Nombre de columna con valores únicos para usar en nombre archivo.
    col_texto: str
        Nombre de columna que contiene texto en sus filas.
    directorio: str | Path
        Directorio en donde se quiere guardar los archivos de texto.

    Returns
    ---------
    None
    """
    salida = Path(directorio).resolve()
    df["nombres"] = df[col_id].apply(lambda x: salida.joinpath(f"{x}.txt"))
    df.apply(lambda x: guardar_texto(x[col_texto], x["nombres"]), axis=1)

    return


class Textos:
    """Colección de textos almacenados en un directorio.

    Itera rutas en directorio, opcionalmente aleatoriamente, y extrae texto y metadata de cada archivo.
    Iteración puede ser el texto de un archivo o cada párrafo en él, filtrando líneas según longitud.
    """

    def __init__(self, directorio, aleatorio=False, chars=0, parrafos=False):
        self.directorio = Path(directorio).resolve()
        self.aleatorio = aleatorio
        self.chars = chars
        self.parrafos = parrafos

    def __repr__(self):
        return f"{self.__len__()} archivos en directorio {self.directorio.name}."

    def __len__(self):
        return len(
            list(
                f
                for f in self.directorio.glob("**/*")
                if f.is_file() and not f.name.startswith(".")
            )
        )

    def __iter__(self):
        """Iterar devuelve texto, meta de cada archivo."""
        for texto, meta in iterar_registros(
            self.directorio,
            aleatorio=self.aleatorio,
            chars=self.chars,
            parrafos=self.parrafos,
        ):
            yield texto, meta
