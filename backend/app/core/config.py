"""
Configuración central de la aplicación.
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Clase de configuración de la aplicación.
    """
    
    # Información de la aplicación
    APP_NAME: str = "Sistema Facturación Galletas"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Base de datos
    DATABASE_URL: str = "sqlite:///./galletas.db"
    
    # Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    
    # Seguridad - JWT
    SECRET_KEY: str = "dev_secret_key_cambiar_en_produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    class Config:
        """Configuración de Pydantic"""
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

# Instancia global de configuración
settings = Settings()
