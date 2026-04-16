"""
Schemas Pydantic para Ventas.

Define la estructura de datos para crear y consultar ventas (facturas).
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


# ========== SCHEMAS DE ITEMS DE VENTA ==========

class SaleItemBase(BaseModel):
    """Schema base para un item de venta"""
    product_id: int = Field(..., description="ID del producto")
    quantity: int = Field(..., gt=0, description="Cantidad (debe ser mayor a 0)")
    discount: Decimal = Field(default=0, ge=0, description="Descuento del item")


class SaleItemCreate(SaleItemBase):
    """Schema para crear un item de venta"""
    pass


class SaleItemResponse(BaseModel):
    """Schema de respuesta de un item de venta"""
    id: int
    product_id: int
    product_name: str = ""  # Se llenará desde el producto
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    discount: Decimal
    total: Decimal
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ========== SCHEMAS DE VENTAS ==========

class SaleBase(BaseModel):
    """Schema base de Venta"""
    customer_id: Optional[int] = Field(None, description="ID del cliente (opcional)")
    payment_method: str = Field(..., description="Método de pago: efectivo, tarjeta, transferencia, credito")
    payment_received: Decimal = Field(..., gt=0, description="Monto recibido")
    discount: Decimal = Field(default=0, ge=0, description="Descuento general de la venta")
    tax: Decimal = Field(default=0, ge=0, description="IVA u otros impuestos")
    notes: Optional[str] = Field(None, description="Notas adicionales")
    
    @field_validator('payment_method')
    @classmethod
    def validate_payment_method(cls, value: str) -> str:
        """Valida que el método de pago sea válido"""
        valid_methods = ['efectivo', 'tarjeta', 'transferencia', 'credito']
        value_lower = value.lower()
        if value_lower not in valid_methods:
            raise ValueError(f'Método de pago inválido. Opciones: {", ".join(valid_methods)}')
        return value_lower


class SaleCreate(SaleBase):
    """
    Schema para crear una venta completa.
    
    Incluye la cabecera de la venta y todos sus items.
    """
    items: List[SaleItemCreate] = Field(..., min_length=1, description="Lista de productos a vender (mínimo 1)")
    
    @field_validator('items')
    @classmethod
    def validate_items(cls, items: List[SaleItemCreate]) -> List[SaleItemCreate]:
        """Valida que haya al menos un item"""
        if not items:
            raise ValueError('Debe incluir al menos un producto en la venta')
        return items


class SaleUpdate(BaseModel):
    """Schema para actualizar una venta (solo campos básicos)"""
    customer_id: Optional[int] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = Field(None, description="Estado: pendiente, completada, anulada")


class SaleResponse(BaseModel):
    """
    Schema de respuesta de una venta completa.
    
    Incluye todos los cálculos y relaciones.
    """
    id: int
    invoice_number: str
    customer_id: Optional[int]
    customer_name: Optional[str] = None  # Se llenará desde la relación
    user_id: int
    user_name: Optional[str] = None  # Se llenará desde la relación
    
    # Totales
    subtotal: Decimal
    tax: Decimal
    discount: Decimal
    total: Decimal
    
    # Pago
    payment_method: str
    payment_received: Decimal
    change_returned: Decimal
    
    # Estado y notas
    status: str
    notes: Optional[str]
    
    # Items de la venta
    items: List[SaleItemResponse] = []
    
    # Fechas
    sale_date: datetime
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class SaleSummary(BaseModel):
    """
    Schema resumido de venta.
    
    Útil para listados donde no necesitas todo el detalle.
    """
    id: int
    invoice_number: str
    customer_name: Optional[str]
    total: Decimal
    payment_method: str
    status: str
    sale_date: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ========== SCHEMAS PARA REPORTES ==========

class SalesStats(BaseModel):
    """Estadísticas de ventas"""
    total_sales: int
    total_amount: Decimal
    pending_sales: int
    completed_sales: int
    cancelled_sales: int
    average_sale: Decimal


class DailySales(BaseModel):
    """Ventas del día"""
    date: str
    total_sales: int
    total_amount: Decimal
    cash_sales: Decimal
    card_sales: Decimal
    transfer_sales: Decimal