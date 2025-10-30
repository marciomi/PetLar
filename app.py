from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'  # Troque por uma chave segura em produção
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelos do Banco de Dados
class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)
    raca = db.Column(db.String(50))
    idade = db.Column(db.Integer)
    tamanho = db.Column(db.String(20))  # pequeno, médio, grande
    energia = db.Column(db.String(20))  # baixa, média, alta
    sociabilidade_criancas = db.Column(db.Boolean, default=False)
    sociabilidade_outros_animais = db.Column(db.Boolean, default=False)
    cuidados_especiais = db.Column(db.String(200))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    disponivel = db.Column(db.Boolean, default=True)
    foto = db.Column(db.String(200))  # caminho para a imagem

class Adotante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(20))
    tipo_residencia = db.Column(db.String(50))  # apartamento, casa com quintal
    tamanho_residencia = db.Column(db.String(50))  # pequeno, médio, grande
    tem_criancas = db.Column(db.Boolean, default=False)
    tem_outros_animais = db.Column(db.Boolean, default=False)
    experiencia_animais = db.Column(db.String(50))  # nenhuma, pouca, muita
    tempo_disponivel = db.Column(db.String(50))  # pouco, moderado, muito
    preferencia_especie = db.Column(db.String(50))
    preferencia_tamanho = db.Column(db.String(50))
    preferencia_energia = db.Column(db.String(50))
    
    def verificar_senha(self, senha):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.senha, senha)
    
# Decorator para rotas protegidas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'adotante_id' not in session:
            flash('Por favor faça login para acessar esta página', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Rotas de Autenticação
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()
        
        if not email or not senha:
            flash('Preencha todos os campos', 'danger')
            return redirect(url_for('login'))
        
        adotante = Adotante.query.filter_by(email=email).first()
        
        if adotante and adotante.verificar_senha(senha):
            session['adotante_id'] = adotante.id
            session['adotante_nome'] = adotante.nome
            flash('Login realizado com sucesso!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('ver_matches'))
        else:
            flash('E-mail ou senha incorretos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você foi desconectado', 'info')
    return redirect(url_for('index'))

# Rotas Principais
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro/animal', methods=['GET', 'POST'])
def cadastro_animal():
    if request.method == 'POST':
        try:
            novo_animal = Animal(
                nome=request.form['nome'],
                especie=request.form['especie'],
                raca=request.form['raca'],
                idade=request.form['idade'],
                tamanho=request.form['tamanho'],
                energia=request.form['energia'],
                sociabilidade_criancas='sociabilidade_criancas' in request.form,
                sociabilidade_outros_animais='sociabilidade_outros_animais' in request.form,
                cuidados_especiais=request.form['cuidados_especiais']
            )
            db.session.add(novo_animal)
            db.session.commit()
            flash('Animal cadastrado com sucesso!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar animal: {str(e)}', 'danger')
    return render_template('cadastro_animal.html')

@app.route('/cadastro/adotante', methods=['GET', 'POST'])
def cadastro_adotante():
    if request.method == 'POST':
        try:
            # Verificação de campos obrigatórios
            required_fields = ['nome', 'email', 'senha', 'tipo_residencia']
            for field in required_fields:
                if field not in request.form or not request.form[field].strip():
                    flash(f'O campo {field} é obrigatório', 'danger')
                    return redirect(url_for('cadastro_adotante'))

            # Verifica se email já existe
            if Adotante.query.filter_by(email=request.form['email']).first():
                flash('Este e-mail já está cadastrado', 'danger')
                return redirect(url_for('cadastro_adotante'))

            # Criação do adotante
            novo_adotante = Adotante(
                nome=request.form['nome'],
                email=request.form['email'],
                senha=generate_password_hash(request.form['senha'], method='scrypt'),
                telefone=request.form.get('telefone', ''),
                tipo_residencia=request.form['tipo_residencia'],
                tamanho_residencia=request.form.get('tamanho_residencia', 'médio'),
                tem_criancas=request.form.get('tem_criancas', 'false').lower() == 'true',
                tem_outros_animais=request.form.get('tem_outros_animais', 'false').lower() == 'true',
                experiencia_animais=request.form.get('experiencia_animais', 'nenhuma'),
                tempo_disponivel=request.form.get('tempo_disponivel', 'moderado'),
                preferencia_especie=request.form.get('preferencia_especie', 'qualquer'),
                preferencia_tamanho=request.form.get('preferencia_tamanho', 'qualquer'),
                preferencia_energia=request.form.get('preferencia_energia', 'qualquer')
            )
            
            db.session.add(novo_adotante)
            db.session.commit()
            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar: {str(e)}', 'danger')
            app.logger.error(f'Erro no cadastro: {str(e)}')

    return render_template('cadastro_adotante.html')

# Algoritmo de Matching
def calcular_compatibilidade(animal, adotante):
    score = 0
    
    # Espécie (20 pontos)
    if animal.especie == adotante.preferencia_especie or adotante.preferencia_especie == 'qualquer':
        score += 20
    
    # Tamanho (20 pontos)
    if animal.tamanho == adotante.preferencia_tamanho or adotante.preferencia_tamanho == 'qualquer':
        score += 20
    elif ((animal.tamanho == "médio" and adotante.preferencia_tamanho == "pequeno") or
          (animal.tamanho == "médio" and adotante.preferencia_tamanho == "grande")):
        score += 10
    
    # Residência (15 pontos)
    if (animal.tamanho == "pequeno" and adotante.tipo_residencia == "apartamento") or \
       (animal.tamanho == "grande" and adotante.tipo_residencia == "casa com quintal"):
        score += 15
    
    # Energia (15 pontos)
    if animal.energia == adotante.preferencia_energia or adotante.preferencia_energia == 'qualquer':
        score += 15
    
    # Crianças (10 pontos)
    if adotante.tem_criancas and animal.sociabilidade_criancas:
        score += 10
    
    # Outros animais (10 pontos)
    if adotante.tem_outros_animais and animal.sociabilidade_outros_animais:
        score += 10
    
    # Experiência (10 pontos)
    if animal.cuidados_especiais and adotante.experiencia_animais == "muita":
        score += 10
    
    return score

@app.route('/matches')
@login_required
def ver_matches():
    adotante_id = session['adotante_id']
    adotante = Adotante.query.get_or_404(adotante_id)
    animais_disponiveis = Animal.query.filter_by(disponivel=True).all()
    
    matches = []
    for animal in animais_disponiveis:
        score = calcular_compatibilidade(animal, adotante)
        compatibilidade = min(100, int(score * 3.3))  # Converte para porcentagem (0-30 vira 0-100)
        
        if compatibilidade >= 50:  # Mostra apenas matches com pelo menos 50% de compatibilidade
            matches.append({
                'animal': animal,
                'compatibilidade': f"{compatibilidade}%",
                'score': score
            })
    
    # Ordena do mais compatível para o menos
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    return render_template('matches.html', 
                         adotante=adotante,
                         matches=matches)

@app.route('/animais')
def listar_animais():
    animais = Animal.query.filter_by(disponivel=True).order_by(Animal.data_cadastro.desc()).all()
    return render_template('lista_animais.html', animais=animais)

# Inicialização do Banco de Dados
with app.app_context():
    db.create_all()
    print("Tabelas verificadas/ criadas com sucesso!")

if __name__ == '__main__':
    app.run(debug=True)
