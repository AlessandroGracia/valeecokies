"""
Configuración central de la aplicación.

Este archivo maneja todas las variables de entorno y configuraciones
usando Pydantic Settings para validación automática.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Clase de configuración de la aplicación.
    
    Pydantic Settings lee automáticamente las variables de entorno
    y las valida según los tipos definidos.
    """
    
    # Información de la aplicación
    APP_NAME: str = "Sistema Facturación Galletas"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Base de datos
    # Por defecto usa SQLite local para desarrollo fácil
    # Para PostgreSQL/Supabase, cambia en .env
    DATABASE_URL: str = "sqlite:///./galletas.db"
    
    # Supabase (OPCIONAL para desarrollo local)
    SUPABASE_URL: Optional[str] = "http://localhost:54321"
    SUPABASE_KEY: Optional[str] = "temporal"
    
    # Seguridad - JWT
    SECRET_KEY: str = "dev_secret_key_cambiar_en_produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 horas (un turno de trabajo)
    
    # Claude AI (OPCIONAL para desarrollo)
    ANTHROPIC_API_KEY: Optional[str] = "temporal"
    
    class Config:
        """Configuración de Pydantic"""
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
# Se carga automáticamente desde .env
settings = Settings()
