import datetime
import os
try:
    from src.modelos.models import db
except:
    from modelos.models import db

class E_Version(db.Model):
    id_version = db.Column(db.Integer, primary_key=True, nullable=False)
    fecha = db.Column(db.String, nullable=False)
    version = db.Column(db.String, nullable=False)
    fe_registrado = db.Column(db.String, nullable=False)

    def __init__(self):
        self.set_values()

    def set_values(self):
        version = os.popen("vcgencmd version")
        sal = []
        for linea in version:
            sal.append(linea)
        self.fecha = sal[0].strip()
        self.version= sal[2].split("version")[1].strip()

    def get_fecha(self):
        return self.fecha

    def get_version(self):
        return self.version

    def get_all(self):
        return {"fecha":self.get_fecha(),"version":self.get_version()}
