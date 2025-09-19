from fastapi import FastAPI
from sqlmodel import Field, SQLModel, Session, create_engine, select
from typing import Optional, List

# 1. Definir tabla de usuarios
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str

# 2. Configuración de la base de datos
DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# 3. Creacion app de FastAPI
app = FastAPI(title="API de Usuarios")

# 4. Creacion de tablas al iniciar
create_db_and_tables()

# 5. Endpoint raíz
@app.get("/")
def root():
    return {"Hola Bienvenido"}

# 6. Endpoints básicos
@app.post("/users/", response_model=User)
def create_user(user: User):
    """Crear un nuevo usuario"""
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

@app.get("/users/", response_model=List[User])
def read_users():
    """Obtener todos los usuarios"""
    with Session(engine) as session:
        return session.exec(select(User)).all()

@app.put("/users/{user_id}", response_model=Optional[User])
def update_user(user_id: int, new_data: User):
    """Actualizar un usuario"""
    with Session(engine) as session:
        db_user = session.get(User, user_id)
        if db_user:
            db_user.username = new_data.username
            db_user.email = new_data.email
            db_user.password = new_data.password
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
        return db_user

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    """Eliminar un usuario"""
    with Session(engine) as session:
        db_user = session.get(User, user_id)
        if db_user:
            session.delete(db_user)
            session.commit()
            return {"ok": True, "message": "Usuario eliminado"}
        return {"ok": False, "message": "Usuario no encontrado"}
