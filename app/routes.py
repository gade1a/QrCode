from flask import session, flash
from .models import Usuario
from flask import current_app as app
from flask import send_file
from flask import render_template, request, send_file, redirect, url_for
from .models import db, QRCode
from PIL import Image
import qrcode
import os
from io import BytesIO
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from .models import Usuario
from . import db

routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
    if 'usuario_id' not in session:
        return redirect(url_for('routes.login'))
    return redirect(url_for('routes.index'))

def index():
    qr_image = None

    if request.method == 'POST':
        dados = request.form.get('entrada')
        cor_qr = request.form.get('cor_qr') or 'black'
        cor_bg = request.form.get('cor_bg') or 'white'
        logo_file = request.files.get('logo')

        if not dados.strip():
            return render_template('index.html', erro="Por favor, insira algum texto ou URL!")

        # Gerar QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(dados)
        qr.make(fit=True)
        img = qr.make_image(fill_color=cor_qr, back_color=cor_bg).convert("RGB")

        # Adicionar logo se houver
        logo_nome = None
        if logo_file and logo_file.filename != '':
            logo_nome = f"logo_{datetime.utcnow().timestamp()}.png"
            logo_path = os.path.join(app.config['UPLOAD_FOLDER'], logo_nome)
            logo_file.save(logo_path)
            logo = Image.open(logo_path).resize((50, 50))
            pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
            img.paste(logo, pos, mask=logo if logo.mode == "RGBA" else None)

        # Salvar imagem gerada
        imagem_nome = f"qrcode_{datetime.utcnow().timestamp()}.png"
        imagem_path = os.path.join(app.config['UPLOAD_FOLDER'], imagem_nome)
        img.save(imagem_path)

        # Salvar no banco de dados
        novo_qr = QRCode(
            dados=dados,
            cor_qr=cor_qr,
            cor_bg=cor_bg,
            logo_nome=logo_nome,
            imagem_nome=imagem_nome
        )
        db.session.add(novo_qr)
        db.session.commit()

        qr_image = imagem_nome

    return render_template('index.html', qr_image=qr_image)

@routes.route('/historico')
def historico():
    if 'usuario_id' not in session:
        flash('Faça login para acessar o histórico.', 'warning')
        return redirect(url_for('login'))

    qrcodes = QRCode.query.order_by(QRCode.criado_em.desc()).all()
    return render_template('historico.html', qrcodes=qrcodes)

@routes.route('/download/<nome>')
def download(nome):
    caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome)
    return send_file(
        caminho,
        as_attachment=True,
        download_name=nome
    )

@routes.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'danger')
            return redirect(url_for('cadastro'))

        novo_usuario = Usuario(nome=nome, email=email)
        novo_usuario.set_senha(senha)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro.html')

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.verificar_senha(senha):
            session.permanent = True  # ← Aqui ativa a sessão persistente
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome
            session['usuario_admin'] = usuario.admin  # ← Se você tiver o campo admin
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Credenciais inválidas.', 'danger')

    return render_template('index.html')

@routes.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da conta.', 'info')
    return redirect(url_for('login'))

@routes.route('/usuarios')
def usuarios():
    lista = Usuario.query.order_by(Usuario.nome).all()
    return render_template('usuarios.html', usuarios=lista)

@routes.route('/redefinir', methods=['GET', 'POST'])
def redefinir():
    if request.method == 'POST':
        email = request.form.get('email')
        nova_senha = request.form.get('nova_senha')
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            usuario.set_senha(nova_senha)
            db.session.commit()
            flash('Senha redefinida com sucesso!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email não encontrado.', 'danger')

    return render_template('redefinir.html')

@routes.route('/index')
def index():
    if 'usuario_id' not in session:
        flash('Faça login para acessar o gerador.', 'warning')
        return redirect(url_for('login'))
    return render_template('index.html')