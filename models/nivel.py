from models import db

class Nivel(db.Model):
    __tablename__ = 'niveles'
    cve_nivel = db.Column(db.Integer, primary_key=True)
    nivel = db.Column(db.String(25), nullable=False)
