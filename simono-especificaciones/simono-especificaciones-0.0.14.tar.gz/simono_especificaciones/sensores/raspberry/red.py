import psutil
import datetime

try:
    from src.modelos.models import db
except:
    from modelos.models import db


class E_Red(db.Model):
    id_lan = db.Column(db.Integer, primary_key=True, nullable=False)
    familia = db.Column(db.String, nullable=False)
    direccion = db.Column(db.String, nullable=False)
    mascara = db.Column(db.String, nullable=False)
    broadcast = db.Column(db.String, nullable=False)
    fe_registrado = db.Column(db.String, nullable=False)

    def __init__(self):
        self.set_lan()

    def set_lan(self):
        lan = psutil.net_if_addrs()["eth0"]
        #print(lan)
        self.familia = lan[0][0]
        self.direccion = lan[0][1]
        self.mascara = lan[0][2]
        self.broadcast = lan[0][3]

    def get_familia(self):
        return self.familia

    def get_direccion(self):
        return self.direccion

    def get_mascara(self):
        return self.mascara

    def get_broadcast(self):
        return self.broadcast

    def get_all(self):
        sal = {"familia":self.get_familia(),"direccion":self.get_direccion(),"mascara":self.get_mascara(),
               "broadcast":self.get_broadcast()}
        return sal

