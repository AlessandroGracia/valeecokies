"""
Modelo de Cliente.

Define la estructura de la tabla 'clientes' para gestión
de clientes del negocio.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Customer(Base):
    """
    Modelo de Cliente.
    
    Almacena información de los clientes del negocio.
    """
    __tablename__ = "clientes"
    
    # Identificador
    id = Column(Integer, primary_key=True, index=True)
    
    # Información personal
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    
    # Identificación (cédula, RUC, pasaporte)
    id_number = Column(String(20), unique=True, nullable=True, index=True)
    
    # Dirección
    address = Column(Text, nullable=True)
    city = Column(String(50), nullable=True)
    
    # Notas adicionales
    notes = Column(Text, nullable=True)
    
    # Estado
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Customer {self.full_name}>"
