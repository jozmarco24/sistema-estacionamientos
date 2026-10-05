import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgrespassword@localhost:5432/db_sistema_estacionamientos")
SCHEMA_NAME = os.getenv("SCHEMA_NAME", "db_usuarios")

engine = create_engine(
    DATABASE_URL,
    connect_args={"options": f"-c search_path={SCHEMA_NAME},public"}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
