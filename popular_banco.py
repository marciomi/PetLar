import random
from datetime import datetime, timedelta
from faker import Faker
from werkzeug.security import generate_password_hash  # Importação adicionada
from app import app, db, Animal, Adotante

fake = Faker('pt_BR')  # Gerador de dados em português

def criar_animais(qtd=50):
    especies = ['cão', 'gato']
    tamanhos = ['pequeno', 'médio', 'grande']
    energias = ['baixa', 'média', 'alta']
    
    for _ in range(qtd):
        animal = Animal(
            nome=fake.first_name(),
            especie=random.choice(especies),
            raca=fake.word().capitalize(),
            idade=random.randint(0, 15),
            tamanho=random.choice(tamanhos),
            energia=random.choice(energias),
            sociabilidade_criancas=random.choice([True, False]),
            sociabilidade_outros_animais=random.choice([True, False]),
            cuidados_especiais=random.choice(['Nenhum', 'Dieta especial', 'Medicação contínua', '']),
            data_cadastro=fake.date_time_this_year(),
            disponivel=random.choice([True, True, True, False])  # 75% de chance de estar disponível
        )
        db.session.add(animal)
    db.session.commit()
    print(f"{qtd} animais criados com sucesso!")

def criar_adotantes(qtd=30):
    tipos_residencia = ['apartamento', 'casa sem quintal', 'casa com quintal']
    experiencias = ['nenhuma', 'pouca', 'muita']
    
    for _ in range(qtd):
        adotante = Adotante(
            nome=fake.name(),
            email=fake.unique.email(),
            senha=generate_password_hash('123456', method='scrypt'),
            telefone=fake.cellphone_number(),
            tipo_residencia=random.choice(tipos_residencia),
            tamanho_residencia=random.choice(['pequeno', 'médio', 'grande']),
            tem_criancas=random.choice([True, False]),
            tem_outros_animais=random.choice([True, False]),
            experiencia_animais=random.choice(experiencias),
            tempo_disponivel=random.choice(['pouco', 'moderado', 'muito']),
            preferencia_especie=random.choice(['cão', 'gato', 'qualquer']),
            preferencia_tamanho=random.choice(['pequeno', 'médio', 'grande', 'qualquer']),
            preferencia_energia=random.choice(['baixa', 'média', 'alta', 'qualquer'])
        )
        db.session.add(adotante)
    db.session.commit()
    print(f"{qtd} adotantes criados com sucesso!")

if __name__ == '__main__':
    with app.app_context():
        print("Limpando banco de dados existente...")
        db.drop_all()
        db.create_all()
        
        print("Criando dados fictícios...")
        criar_animais(50)
        criar_adotantes(30)
        
        print("Banco de dados populado com sucesso!")
