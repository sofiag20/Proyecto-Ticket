from models import db

class Asunto(db.Model):
    __tablename__ = 'asuntos'
    id_asunto = db.Column(db.Integer, primary_key=True)
    asunto = db.Column(db.String(50), nullable=False)
