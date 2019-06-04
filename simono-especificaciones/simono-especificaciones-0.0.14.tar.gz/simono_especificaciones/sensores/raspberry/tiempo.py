import datetime
import psutil
try:
    from src.modelos.models import db
except:
    from modelos.models import db

class E_Inicio(db.Model):
    id_inicio = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.Float, nullable=False)
    fecha_inicio = db.Column(db.String, nullable=False)
    fe_registrado = db.Column(db.String, nullable=False)

    def __init__(self):
        self.value = self.valor()
        self.fecha_inicio = self.get_time()

    def get_value(self):
        return self.value

    def get_fecha_inicio(self):
        return self.fecha_inicio

    def valor(self):
        return psutil.boot_time()

    def get_time(self):
        return datetime.datetime.fromtimestamp(self.valor()).strftime("%Y-%m-%d %H:%M:%S")

    def get_all(self):
        return {"valor":self.get_value(),"inicio":self.get_fecha_inicio()}