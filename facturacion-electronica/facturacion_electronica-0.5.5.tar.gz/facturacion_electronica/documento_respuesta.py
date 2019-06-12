# -*- coding: utf-8 -*-
class UserError(Exception):
    """Clase perdida"""
    pass


class Warning(Exception):
    """Clase perdida"""
    pass


class Respuesta(object):

    def __init__(self, vals):
        self.id_respuesta = vals['id_respuesta']
        self.recinto = vals['recinto']
        self.telefono = vals['telefono']
        self.email = vals['email']
        self.nombre = vals['nombre']
        self.respuesta = vals['respuesta']
        self.glosa = vals['glosa']
