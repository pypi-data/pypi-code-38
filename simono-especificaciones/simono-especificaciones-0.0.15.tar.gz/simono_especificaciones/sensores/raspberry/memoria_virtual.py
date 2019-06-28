import psutil
import datetime

try:
    from src.modelos.models import db
except:
    from modelos.models import db


class E_Memoria_Virtual(db.Model):
    id_mem_virt = db.Column(db.Integer, primary_key=True, nullable=False)
    total = db.Column(db.Float, nullable=False)
    disponible = db.Column(db.Float, nullable=False)
    usada = db.Column(db.Float, nullable=False)
    libre = db.Column(db.Float, nullable=False)
    porcentaje = db.Column(db.Float, nullable=False)
    fe_registrado = db.Column(db.String, nullable=False)

    def __init__(self):
        self.set_info_mem_virt()

    def set_info_mem_virt(self):
        mem_virt = psutil.virtual_memory()
        self.total = mem_virt.total
        self.usada = mem_virt.used
        self.libre = mem_virt.free
        self.disponible = mem_virt.available
        self.porcentaje = mem_virt.percent

    def get_total(self):
        return self.total

    def get_usada(self):
        return self.usada

    def get_libre(self):
        return self.libre

    def get_disponible(self):
        return self.disponible

    def get_porcentaje(self):
        return self.porcentaje

    def get_all(self):
        sal = {"total": self.get_total(), "usada": self.get_usada(), "libre": self.get_libre(),
               "disponible": self.get_disponible(), "porcentaje": self.get_porcentaje()}
        return sal

