"""
Schemas Pydantic para Clientes.

Define la estructura de datos para crear, actualizar y consultar clientes.
"""

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class CustomerBase(BaseModel):
    """
    Schema base de Cliente.
    
    Contiene los campos comunes para crear y actualizar.
    """
    full_name: str = Field(..., min_length=1, max_length=100, description="Nombre completo del cliente")
    email: Optional[EmailStr] = Field(None, description="Email del cliente")
    phone: Optional[str] = Field(None, max_length=20, description="Teléfono del cliente")
    id_number: Optional[str] = Field(None, max_length=20, description="Cédula o RUC")
    address: Optional[str] = Field(None, description="Dirección completa")
    city: Optional[str] = Field(None, max_length=50, description="Ciudad")
    notes: Optional[str] = Field(None, description="Notas adicionales")
    is_active: bool = Field(default=True, description="Estado activo/inactivo")


class CustomerCreate(CustomerBase):
    """
    Schema para crear un cliente.
    
    Hereda todos los campos de CustomerBase.
    """
    pass


class CustomerUpdate(BaseModel):
    """
    Schema para actualizar un cliente.
    
    Todos los campos son opcionales (actualización parcial).
    """
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    id_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerResponse(CustomerBase):
    """
    Schema de respuesta del cliente.
    
    Incluye campos adicionales de la base de datos.
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Configuración de Pydantic v2
    model_config = ConfigDict(from_attributes=True)


class CustomerSummary(BaseModel):
    """
    Schema resumido de cliente.
    
    Útil para listas y dropdowns donde no necesitas toda la info.
    """
    id: int
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
