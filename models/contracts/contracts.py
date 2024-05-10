from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from utilities.extensions import db

class CPContract(db.Model):
    __tablename__ = 'cp_contracts'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer)
    chave = db.Column(db.String)
    tipo = db.Column(db.Integer)
    nome = db.Column(db.String)
    cpf_cnpj = db.Column(db.Integer)
    contract_code = db.Column(db.String)
    indice = db.Column(db.Integer)
    parcelas = db.Column(db.String)
    lote = db.Column(db.String)
    empreendimento = db.Column(db.String)
    client_id = db.Column(db.Integer, db.ForeignKey('cp_clients.id'))
    development_site_id = db.Column(db.Integer, db.ForeignKey('cp_development_sites.id'))
    
class CPContractsImport(db.Model):
    __tablename__ = 'cp_contracts_import'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer)
    file_name = db.Column(db.String)
    total_clients_imported = db.Column(db.Integer, default=0)
    total_clients_for_update = db.Column(db.Integer, default=0)
    total_clients_for_insert = db.Column(db.Integer, default=0)
    total_contracts_imported = db.Column(db.Integer, default=0)
    total_contracts_for_insert = db.Column(db.Integer, default=0)
    total_contracts_for_update = db.Column(db.Integer, default=0)
    status = db.Column(db.String, default="Pendente")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class CPContractStage(db.Model):
    __tablename__ = 'cp_contracts_stage'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer)
    tipo = db.Column(db.Integer)
    contract_code = db.Column(db.String(255))
    parcelas = db.Column(db.String(255))
    unidades = db.Column(db.String(255))
    load_file_name = db.Column(db.String(255))
    empreendimento = db.Column(db.String(255))
    doc = db.Column(db.String)
    development_site_id = db.Column(db.Integer)
    import_id = db.Column(db.Integer)
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class CPDevelopmentSite(db.Model):
    __tablename__ = 'cp_development_sites'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer)
    name = db.Column(db.String(255))
    site_sector = db.Column(db.Integer)
    site_num = db.Column(db.Integer)
    wp_id = db.Column(db.Integer)
    wp_status = db.Column(db.String(255))
    wp_construct_status = db.Column(db.Integer)
    wp_tp_status = db.Column(db.Integer)
    wp_pv_status = db.Column(db.Integer)
    wp_eg_status = db.Column(db.Integer)
    wp_en_status = db.Column(db.Integer)
    wp_addr = db.Column(db.String(255))
    wp_gallery = db.Column(db.String(255))  # Assuming gallery URL or comma-separated URLs

    def __repr__(self):
        return f'<CPDevelopmentSite {self.name}>'