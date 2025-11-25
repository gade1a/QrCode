from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class QRCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dados = db.Column(db.Text, nullable=False)
    cor_qr = db.Column(db.String(20))
    cor_bg = db.Column(db.String(20))
    logo_nome = db.Column(db.String(120))
    imagem_nome = db.Column(db.String(120))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    admin = db.Column(db.Boolean, default=False)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    senha_hash = db.Column(db.Text, nullable=False)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)