from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SolicitudTurno(db.Model):
    __tablename__ = 'solicitud_turno'
    
    nombre_completo = db.Column(db.String(50), nullable=False)
    curp = db.Column(db.String(18), primary_key=True)
    id_asunto = db.Column(db.Integer, nullable=False)
    cve_nivel = db.Column(db.Integer, nullable=False)
    cve_mun = db.Column(db.Integer, nullable=False)
    nombre = db.Column(db.String(23), nullable=False)
    paterno = db.Column(db.String(50))
    materno = db.Column(db.String(50))
    tel = db.Column(db.String(43))
    celular = db.Column(db.String(20))
    correo = db.Column(db.String(43))
    turno = db.Column(db.Integer, nullable=False)
    id_estatus = db.Column(db.Integer, default=1)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    
