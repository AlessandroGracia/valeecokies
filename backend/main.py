"""
Archivo principal de la aplicación FastAPI.

Este es el punto de entrada de todo el backend.
Aquí se configura la aplicación y se registran las rutas.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base

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
    description="""
    ## API REST para Sistema de Facturación de Galletas 🍪
    
    Sistema completo con:
    - ✅ Gestión de Productos
    - ✅ Gestión de Clientes
    - ✅ Facturación completa
    - ✅ Punto de Venta (POS)
    - ✅ Caja Diaria
    - 🔜 Integración con IA (Claude)
    - 🔜 Autenticación JWT
    
    **Endpoints disponibles:**
    - `/api/products` - CRUD de productos
    - `/api/customers` - CRUD de clientes
    - `/api/sales` - Facturación y ventas
    - `/api/cash-register` - Caja diaria
    - `/api/pos` - Punto de venta
    """,
    docs_url="/docs",  # Documentación Swagger en /docs
    redoc_url="/redoc"  # Documentación alternativa en /redoc
)

# Configuración de CORS
# Permitimos todos los orígenes para que el .exe (file://) pueda conectarse.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== ENDPOINTS RAÍZ ==========

@app.get("/")
async def root():
    """
    Endpoint raíz de bienvenida.
    
    Útil para verificar que la API está funcionando.
    """
    return {
        "message": f"Bienvenido a {settings.APP_NAME} 🍪",
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
        "endpoints": {
            "products": "/api/products",
            "customers": "/api/customers",
            "sales": "/api/sales",
            "cash_register": "/api/cash-register",
            "pos": "/api/pos"
        },
        "features": {
            "facturacion": "✅ Activa",
            "inventario": "✅ Activo",
            "clientes": "✅ Activo",
            "caja_diaria": "✅ Activa",
            "pos": "✅ Activo",
            "ia_integration": "🔜 Próximamente",
            "autenticacion": "🔜 Próximamente"
        }
    }


@app.get("/health")
async def health_check():
    """
    Endpoint de salud del sistema.
    
    Se usa para monitoreo y verificar que todo funciona correctamente.
    """
    return {
        "status": "healthy",
        "database": "connected",
        "app_name": settings.APP_NAME,
        "version": settings.VERSION
    }


# ========== REGISTRAR ROUTERS ==========

# Registrar router de productos
app.include_router(products_router)

# Registrar router de clientes
app.include_router(customers_router)

# Registrar router de ventas
app.include_router(sales_router)

# Registrar router de caja diaria
app.include_router(cash_register_router)

# Registrar router de punto de venta
app.include_router(pos_router)

# Registrar autenticación
from app.api.auth import router as auth_router
app.include_router(auth_router)


if __name__ == "__main__":
    import uvicorn
    # Ejecutar el servidor
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG  # Auto-reload en modo debug
    )