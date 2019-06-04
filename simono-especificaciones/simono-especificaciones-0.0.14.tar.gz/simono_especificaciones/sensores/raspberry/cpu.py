import psutil
import datetime

try:
    from src.modelos.models import db
except:
    from modelos.models import db

class E_Cpu(db.Model):
    id_cpu = db.Column(db.Integer, primary_key=True, nullable=False)
    porcentaje = db.Column(db.Float, nullable=False)
    fe_registrado = db.Column(db.String, nullable=False)

    def __init__(self):
        self.porcentaje = self.get_cpu_porcentaje()

    def get_cpu_porcentaje(self):
        return psutil.cpu_percent(interval=1)
    