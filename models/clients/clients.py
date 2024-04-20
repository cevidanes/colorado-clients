from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from utilities.extensions import db

class CPClient(db.Model):
    __tablename__ = 'cp_clients'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer)
    name = db.Column(db.String(255))
    cpf_cnpj = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('cp_users.id'))
    
class CPClientStage(db.Model):
    __tablename__ = 'cp_clients_stages'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer)
    name = db.Column(db.String(255))
    cpf_cnpj = db.Column(db.String)
    import_id = db.Column(db.Integer, db.ForeignKey('cp_contracts_import.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('cp_users.id'))