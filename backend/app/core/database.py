"""
Configuración de la base de datos usando SQLAlchemy.
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import os

def _create_engine():
    """Crea el motor de base de datos con diagnóstico profundo."""
    
    # 1. Diagnóstico de variables de entorno (Solo nombres y longitud por seguridad)
    env_keys = list(os.environ.keys())
    db_env = os.environ.get("DATABASE_URL")
    
    print(f"DIAGNÓSTICO: Variables encontradas: {len(env_keys)}")
    print(f"DIAGNÓSTICO: DATABASE_URL presente en os.environ: {db_env is not None}")
    
    # URL a usar
    raw_url = db_env or settings.DATABASE_URL
    
    # 2. Corregir protocolo
    if raw_url.startswith("postgresql://"):
        db_url = raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
    else:
        db_url = raw_url
    
    is_cloud = "postgresql" in db_url or "psycopg" in db_url

    try:
        eng = create_engine(
            db_url,
            pool_pre_ping=True,
            echo=False
        )
        # Probar conexión real
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
            
        print(f"CONECTADO EXITOSAMENTE A: {'PostgreSQL' if is_cloud else 'SQLite'}")
        return eng
        
    except Exception as e:
        print(f"ERROR CRÍTICO AL CONECTAR: {str(e)}")
        # Solo caemos a SQLite si estamos en local
        if not is_cloud:
            return create_engine("sqlite:///./galletas.db")
        # Si es nube y falló, dejamos que falle el deploy para ver el error en Render
        raise e

# Crear el motor
engine = _create_engine()

# Fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para todos los modelos
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
