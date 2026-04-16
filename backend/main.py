"""
Aplicación Principal FastAPI - POS Galletas.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, products, customers, sales, cash_register_router, pos_router
from app.core.database import engine, Base
import os

app = FastAPI(
    title="Sistema de Facturación Galletas API",
    description="Backend para el sistema POS de galletas",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Endpoint de Salud para Render
@app.get("/health")
def health_check():
    return {"status": "ok", "environment": "production"}

# Endpoint de diagnóstico profundo
@app.get("/api/debug-db")
def debug_db():
    from sqlalchemy import text
    import os
    from datetime import datetime
    
    db_info = "Desconocido"
    users_count = 0
    error = None
    
    try:
        with engine.connect() as conn:
            if "postgresql" in str(engine.url) or "psycopg" in str(engine.url):
                db_info = "PostgreSQL (Nube)"
            else:
                db_info = "SQLite (Local)"
            result = conn.execute(text("SELECT count(*) FROM usuarios"))
            users_count = result.scalar()
    except Exception as e:
        error = str(e)
        
    return {
        "status": "OK (Conectado)" if not error else "Error",
        "database_detected": db_info,
        "users_found": users_count,
        "error": error,
        "server_time": datetime.now().isoformat(),
        "host_info": os.environ.get("DATABASE_URL", "SQLite").split("@")[-1] if "@" in os.environ.get("DATABASE_URL", "") else "local"
    }

# Incluir rutas de la API con los nombres correctos
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(products.router, prefix="/api/items", tags=["Productos"])
app.include_router(customers.router, prefix="/api/customers", tags=["Clientes"])
app.include_router(sales.router, prefix="/api/sales", tags=["Ventas"])
app.include_router(cash_register_router.router, prefix="/api/cash", tags=["Caja"])
app.include_router(pos_router.router, prefix="/api/pos", tags=["POS"])

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API del Sistema de Galletas"}