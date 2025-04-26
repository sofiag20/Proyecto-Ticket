from models import db

class Municipio(db.Model):
    __tablename__ = 'municipios'
    cve_mun = db.Column(db.Integer, primary_key=True)
    nombre_mun = db.Column(db.String(30), nullable=False)

