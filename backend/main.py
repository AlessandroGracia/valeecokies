"""
Archivo principal de la aplicación FastAPI.

Este es el punto de entrada de todo el backend.
Aquí se configura la aplicación y se registran las rutas.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.models.user import User

# Importar routers
from app.api.products import router as products_router
from app.api.customers import router as customers_router
from app.api.sales import router as sales_router
from app.api.cash_register_router import router as cash_register_router
from app.api.pos_router import router as pos_router

# Crear todas las tablas en la base de datos
# (En producción usarías Alembic para migraciones)
Base.metadata.create_all(bind=engine)

# Crear instancia de FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== ENDPOINTS DE DIAGNÓSTICO ==========

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/")
def read_root():
    return {
        "message": f"Bienvenido a {settings.APP_NAME} 🍪",
        "version": settings.VERSION,
        "status": "online"
    }

@app.get("/api/debug-db")
def debug_db():
    from sqlalchemy import text
    db_type = "Desconocido"
    user_count = 0
    db_status = "Error"
    error_msg = None
    
    try:
        # Detectar tipo de DB desde la URL
        db_url = str(engine.url)
        if "postgresql" in db_url or "psycopg" in db_url:
            db_type = "PostgreSQL (Nube)"
        else:
            db_type = "SQLite (Local)"
            
        # Probar conexión y contar usuarios
        with SessionLocal() as db:
            user_count = db.query(User).count()
            db_status = "OK (Conectado)"
    except Exception as e:
        db_status = "Error de Conexión"
        error_msg = str(e)
        
    return {
        "status": db_status,
        "database_detected": db_type,
        "users_found": user_count,
        "error": error_msg,
        "server_time": datetime.now().isoformat(),
        "host_info": str(engine.url).split("@")[-1] if "@" in str(engine.url) else "local"
    }

# ========== REGISTRAR ROUTERS ==========

app.include_router(products_router)
app.include_router(customers_router)
app.include_router(sales_router)
app.include_router(cash_register_router)
app.include_router(pos_router)

# Registrar autenticación
from app.api.auth import router as auth_router
app.include_router(auth_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)