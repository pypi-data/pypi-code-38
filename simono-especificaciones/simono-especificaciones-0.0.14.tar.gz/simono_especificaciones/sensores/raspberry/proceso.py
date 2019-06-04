import datetime
try:
    from src.modelos.models import db
except:
    from modelos.models import db

class E_Proceso(db.Model):
    id_proceso = db.Column(db.Integer, primary_key=True, nullable=False)
    pid = db.Column(db.Integer, nullable=False)
    fecha_inicio = db.Column(db.String, nullable=False)
    proceso = db.Column(db.String, nullable=False)
    usuario = db.Column(db.String, nullable=False)
    fecha_c = db.Column(db.String, nullable=False)
    estado = db.Column(db.String, nullable=False)
    fe_registrado = db.Column(db.String, nullable=False)