"""
Configuración de la base de datos usando SQLAlchemy.

Soporta SQLite (desarrollo local) y PostgreSQL (Supabase/producción).
Si PostgreSQL no está disponible, cae automáticamente a SQLite.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import os

def _create_engine():
    """Crea el motor de base de datos buscando la URL en el sistema."""
    
    # 1. Buscar DATABASE_URL en variables de entorno (Prioridad Render)
    db_url = os.environ.get("DATABASE_URL") or os.environ.get("database_url") or settings.DATABASE_URL
    
    # 2. Corregir protocolo para SQLAlchemy + Psycopg3
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    
    is_cloud = "postgresql" in db_url or "psycopg" in db_url

    try:
        eng = create_engine(
            db_url,
            pool_pre_ping=True,
            echo=False
        )
        # Probar conexión simple
        with eng.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
            
        if is_cloud:
            print("CONECTADO: PostgreSQL (Supabase) listo.")
        else:
            print("CONECTADO: SQLite local listo.")
            
        return eng
    except Exception as e:
        print(f"ERROR DE CONEXIÓN: {str(e)}")
        # Si falló PostgreSQL, intentar SQLite como último recurso
        if is_cloud:
            print("FALLBACK: Usando SQLite temporal por fallo en Postgres.")
            return _create_sqlite_engine("sqlite:///./galletas.db")
        raise e

def _create_sqlite_engine(url):
    """Crea motor SQLite con configuraciones apropiadas."""
    eng = create_engine(
        url,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    @event.listens_for(eng, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    return eng

# Crear el motor
engine = _create_engine()

# Fábrica de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Clase base para todos los modelos
Base = declarative_base()

def get_db():
    """Generador de sesiones de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
