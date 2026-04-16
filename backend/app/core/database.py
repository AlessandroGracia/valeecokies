"""
Configuración de la base de datos usando SQLAlchemy.

Soporta SQLite (desarrollo local) y PostgreSQL (Supabase/producción).
Si PostgreSQL no está disponible, cae automáticamente a SQLite.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Detectar si estamos usando SQLite o PostgreSQL
is_sqlite = settings.DATABASE_URL.startswith("sqlite")


def _create_engine():
    """Crea el motor de base de datos con fallback a SQLite."""
    
    if is_sqlite:
        return _create_sqlite_engine(settings.DATABASE_URL)
    
    # Intentar conectar a PostgreSQL
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    
    try:
        eng = create_engine(
            db_url,
            pool_pre_ping=True,
            echo=settings.DEBUG
        )
        # Probar conexión
        with eng.connect() as conn:
            conn.execute(__import__('sqlalchemy').text("SELECT 1"))
        print("CONECTADO: Conectado a PostgreSQL (Supabase)")
        return eng
    except Exception as e:
        print("ERROR: No se pudo conectar a PostgreSQL: " + str(e))
        print("FALLBACK: Usando SQLite local como fallback (galletas.db)")
        return _create_sqlite_engine("sqlite:///./galletas.db")


def _create_sqlite_engine(url):
    """Crea motor SQLite con configuraciones apropiadas."""
    eng = create_engine(
        url,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG
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
    """
    Generador de sesiones de base de datos.
    
    Se usa como dependencia en FastAPI para inyectar
    automáticamente la sesión en cada endpoint.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
