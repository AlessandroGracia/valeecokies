"""
Schemas Pydantic para Productos.

Los schemas definen la estructura de datos para:
- Entrada de datos (al crear/actualizar)
- Salida de datos (al consultar)

Pydantic valida automáticamente los tipos de datos.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductBase(BaseModel):
    """
    Schema base de Producto.
    
    Contiene los campos comunes para crear y actualizar.
    """
    code: str = Field(..., min_length=1, max_length=20, description="Código único del producto")
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del producto")
    description: Optional[str] = Field(None, description="Descripción del producto")
    category: str = Field("cookies", min_length=1, max_length=50, description="Categoría del producto (cookies, bebidas, postres)")
    cost_price: Decimal = Field(..., gt=0, description="Precio de costo (debe ser mayor a 0)")
    sale_price: Decimal = Field(..., gt=0, description="Precio de venta (debe ser mayor a 0)")
    stock_quantity: int = Field(default=0, ge=0, description="Cantidad en stock")
    min_stock: int = Field(default=10, ge=0, description="Stock mínimo para alertas")
    unit: str = Field(default="unidad", max_length=20, description="Unidad de medida")
    is_active: bool = Field(default=True, description="Estado activo/inactivo")
    
    @field_validator('sale_price')
    @classmethod
    def validate_sale_price(cls, sale_price: Decimal, info) -> Decimal:
        """
        Valida que el precio de venta sea mayor al de costo.
        
        Esta es una regla de negocio: no debes vender por debajo del costo.
        """
        # info.data contiene los otros campos ya validados
        cost_price = info.data.get('cost_price')
        
        if cost_price and sale_price < cost_price:
            raise ValueError('El precio de venta debe ser mayor al precio de costo')
        
        return sale_price


class ProductCreate(ProductBase):
    """
    Schema para crear un producto.
    
    Hereda todos los campos de ProductBase.
    No incluye ID porque se genera automáticamente.
    """
    pass


class ProductUpdate(BaseModel):
    """
    Schema para actualizar un producto.
    
    Todos los campos son opcionales (solo se actualiza lo que se envía).
    """
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    cost_price: Optional[Decimal] = Field(None, gt=0)
    sale_price: Optional[Decimal] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    min_stock: Optional[int] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """
    Schema de respuesta del producto.
    
    Incluye campos calculados y de la base de datos.
    Este es el formato que se envía al frontend.
    """
    id: int
    needs_restock: bool
    profit_margin: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Configuración de Pydantic v2
    model_config = ConfigDict(from_attributes=True)


class StockAdjustment(BaseModel):
    """
    Schema para ajustar el stock de un producto.
    
    Se usa cuando se ingresa o egresa inventario manualmente.
    """
    quantity_change: int = Field(
        ..., 
        description="Cantidad a ajustar (positivo=ingreso, negativo=egreso)"
    )
    reason: Optional[str] = Field(
        None, 
        max_length=200,
        description="Razón del ajuste (opcional)"
    )