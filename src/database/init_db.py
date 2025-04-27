from src.database.config import Base, engine
from src.models.user import User
from sqlalchemy.orm import Session
from src.database.config import SessionLocal

def init_db():
    # Cria as tabelas
    Base.metadata.create_all(bind=engine)

    # Cria um usuário de exemplo
    db = SessionLocal()
    try:
        # Verifica se já existe um usuário
        user = db.query(User).first()
        if not user:
            # Cria um usuário de exemplo
            user = User(
                email="admin@gwan.com.br",
                username="admin",
                hashed_password="admin123",  # Em produção, use senhas criptografadas
                is_active=True
            )
            db.add(user)
            db.commit()
            print("Usuário de exemplo criado com sucesso!")
    except Exception as e:
        print(f"Erro ao criar usuário de exemplo: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Inicializando banco de dados...")
    init_db()
    print("Banco de dados inicializado com sucesso!") 