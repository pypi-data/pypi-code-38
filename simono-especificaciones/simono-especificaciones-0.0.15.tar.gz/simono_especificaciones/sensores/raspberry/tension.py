import os
import datetime

try:
    from src.modelos.models import db
except:
    from modelos.models import db

class E_Tension(db.Model):
    id_tension = db.Column(db.Integer, primary_key=True, nullable=False)
    sdram_i = db.Column(db.Float, nullable=False)
    sdram_p = db.Column(db.Float, nullable=False)
    sdram_c = db.Column(db.Float, nullable=False)
    core = db.Column(db.Float, nullable=False)
    fe_registrado = db.Column(db.String, nullable=False)

    def __init__(self):
        self.core = self.get_core()
        self.sdram_c = self.get_sdram_c()
        self.sdram_i = self.get_sdram_i()
        self.sdram_p = self.get_sdram_p()

    def get_core(self):
        """core = CPU/GPU core"""
        core = os.popen("vcgencmd measure_volts core").read()
        core = (core.replace("volt=", "").replace("V", "")).strip()
        return float(core)

    def get_sdram_i(self):
        """sdram_i = Input/Output"""
        sdram_i = os.popen("vcgencmd measure_volts sdram_i").read()
        sdram_i = (sdram_i.replace("volt=", "").replace("V", "")).strip()
        return float(sdram_i)

    def get_sdram_c(self):
        """sdram_c = controller"""
        sdram_c = os.popen("vcgencmd measure_volts sdram_c").read()
        sdram_c = (sdram_c.replace("volt=", "").replace("V", "")).strip()
        return float(sdram_c)

    def get_sdram_p(self):
        """sdram_p = physical"""
        sdram_p = os.popen("vcgencmd measure_volts sdram_p").read()
        sdram_p = (sdram_p.replace("volt=", "").replace("V", "")).strip()
        return float(sdram_p)

    def get_all(self):
        sal = {"core": self.get_core(), "sdram_i": self.get_sdram_i(), "sdram_c": self.get_sdram_c(),
               "sdram_p": self.get_sdram_p()}
        return sal