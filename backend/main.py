"""
Aplicación Principal FastAPI - POS Galletas.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, items, customers, sales, cash_register, stats
from app.core.database import engine, Base, SessionLocal
import os

# Crear tablas si no existen (solo para SQLite, en Postgres se asume esquema listo)
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Facturación Galletas API",
    description="Backend para el sistema POS de galletas",
    version="1.0.0"
)

# Configuración de CORS - MUY IMPORTANTE PARA PRODUCCIÓN
# Permitimos todos los orígenes, métodos y cabeceras para máxima compatibilidad
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, # Debe ser False si origins es ["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Endpoint de Salud (Healthcheck) para Render
@app.get("/health")
def health_check():
    return {"status": "ok", "environment": "production" if os.environ.get("DATABASE_URL") else "development"}

# Endpoint de diagnóstico profundo
@app.get("/api/debug-db")
def debug_db():
    from sqlalchemy import text
    import os
    
    db_info = "Desconocido"
    users_count = 0
    error = None
    
    try:
        with engine.connect() as conn:
            # Detectar tipo de DB
            if "postgresql" in str(engine.url) or "psycopg" in str(engine.url):
                db_info = "PostgreSQL (Nube)"
            else:
                db_info = "SQLite (Local)"
                
            # Contar usuarios
            result = conn.execute(text("SELECT count(*) FROM usuarios"))
            users_count = result.scalar()
    except Exception as e:
        error = str(e)
        
    return {
        "status": "OK (Conectado)" if not error else "Error",
        "database_detected": db_info,
        "users_found": users_count,
        "error": error,
        "server_time": func.now() if hasattr(func, 'now') else "Ver logs",
        "host_info": os.environ.get("DATABASE_URL", "SQLite").split("@")[-1] if "@" in os.environ.get("DATABASE_URL", "") else "local"
    }

# Incluir rutas de la API
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(items.router, prefix="/api/items", tags=["Productos"])
app.include_router(customers.router, prefix="/api/customers", tags=["Clientes"])
app.include_router(sales.router, prefix="/api/sales", tags=["Ventas"])
app.include_router(cash_register.router, prefix="/api/cash", tags=["Caja"])
app.include_router(stats.router, prefix="/api/stats", tags=["Estadísticas"])

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API del Sistema de Galletas"}