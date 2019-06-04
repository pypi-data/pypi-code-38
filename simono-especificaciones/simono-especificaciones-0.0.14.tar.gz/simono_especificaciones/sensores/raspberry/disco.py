import psutil
import datetime

try:
    from src.modelos.models import db
except:
    from modelos.models import db

class E_Disco(db.Model):
    id_disco = db.Column(db.Integer, primary_key=True, nullable=False)
    total = db.Column(db.Float, nullable=False)
    usada = db.Column(db.Float, nullable=False)
    libre = db.Column(db.Float, nullable=False)
    porcentaje = db.Column(db.Float, nullable=False)
    fe_registrado = db.Column(db.String, nullable=False)

    def __init__(self):
        self.set_info_disk()

    def set_info_disk(self):
        disk = psutil.disk_usage('/')
        self.total = disk.total
        self.usada = disk.used
        self.libre = disk.free
        self.porcentaje = disk.percent

    def get_total(self):
        return self.total

    def get_usada(self):
        return self.usada

    def get_libre(self):
        return self.libre

    def get_porcentaje(self):
        return self.porcentaje

    def get_all(self):
        sal = {"total": self.get_total(), "usada": self.get_usada(), "libre": self.get_libre(),
               "porcentaje": self.get_porcentaje()}
        return sal
