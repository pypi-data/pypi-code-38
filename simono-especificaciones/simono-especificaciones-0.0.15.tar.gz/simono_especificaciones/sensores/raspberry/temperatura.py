import os
import datetime

try:
    from src.modelos.models import db
except:
    from modelos.models import db

class E_Temperatura(db.Model):
    id_temperatura = db.Column(db.Integer, primary_key=True, nullable=False)
    temperatura = db.Column(db.Float, nullable=False)
    unidad = db.Column(db.String, nullable=False)
    fe_registrado = db.Column(db.String, nullable=False)

    def __init__(self):
        self.temperatura = self.get_temperatura()
        self.unidad = "C"

    def get_temperatura(self):
        temp = os.popen("vcgencmd measure_temp").readline()
        temp = (temp.replace("temp=", "").replace("'C", "")).strip()
        return float(temp)

    def get_grados(self):
        return self.unidad

    def get_all(self):
        return {"temperatura":self.get_temperatura(),"grados":self.get_grados()}