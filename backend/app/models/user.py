"""
Modelo de Usuario para la base de datos.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(enum.Enum):
    """
    Enumeración de roles de usuario.
    Nota: Usamos nombres en minúsculas para coincidir exactamente con la DB.
    """
    admin = "admin"
    vendedor = "vendedor"


class User(Base):
    """
    Modelo de Usuario.
    """
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    
    # Rol del usuario
    role = Column(
        Enum(UserRole),
        default=UserRole.vendedor,
        nullable=False
    )
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User {self.username} ({self.role.value})>"
