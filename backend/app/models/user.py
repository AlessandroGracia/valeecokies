"""
Modelo de Usuario para la base de datos.

Este archivo define la estructura de la tabla 'usuarios' 
usando SQLAlchemy ORM.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(enum.Enum):
    """
    Enumeración de roles de usuario.
    
    - ADMIN: Acceso completo al sistema
    - VENDEDOR: Solo facturación y consultas
    """
    ADMIN = "admin"
    VENDEDOR = "vendedor"


class User(Base):
    """
    Modelo de Usuario.
    
    Representa un usuario del sistema (admin o vendedor).
    """
    __tablename__ = "usuarios"
    
    # Columnas de la tabla
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    
    # Rol del usuario
    role = Column(
        Enum(UserRole),
        default=UserRole.VENDEDOR,
        nullable=False
    )
    
    # Estado
    is_active = Column(Boolean, default=True)
    
    # Timestamps automáticos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        """Representación en string del usuario"""
        return f"<User {self.username} ({self.role.value})>"
