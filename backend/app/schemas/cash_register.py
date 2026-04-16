"""
Schemas para el sistema de Caja Diaria.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal


# ========== INVENTARIO DIARIO ==========

class DailyInventoryItem(BaseModel):
    """Schema para un item de inventario diario"""
    product_id: int
    product_name: Optional[str] = None
    initial_stock: int = Field(..., ge=0)
    current_stock: Optional[int] = None
    units_sold: Optional[int] = None


class DailyInventoryCreate(BaseModel):
    """Schema para crear inventario al abrir caja"""
    items: List[DailyInventoryItem] = Field(..., min_length=1)


# ========== MERMAS ==========

class ShrinkageCreate(BaseModel):
    """Schema para registrar una merma"""
    product_id: int
    quantity: int = Field(..., gt=0)
    reason: str = Field(..., min_length=1, max_length=200)
    notes: Optional[str] = None


class ShrinkageResponse(BaseModel):
    """Schema de respuesta de merma"""
    id: int
    product_id: int
    product_name: Optional[str] = None
    quantity: int
    reason: str
    notes: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ========== CAJA DIARIA ==========

class CashRegisterOpen(BaseModel):
    """Schema para abrir caja"""
    initial_cash: Decimal = Field(default=0, ge=0, description="Efectivo inicial en caja")
    inventory_items: List[DailyInventoryItem] = Field(..., min_length=1, description="Inventario inicial del día")


class CashRegisterClose(BaseModel):
    """Schema para cerrar caja"""
    actual_cash: Decimal = Field(..., ge=0, description="Efectivo real contado")
    closing_notes: Optional[str] = Field(None, description="Notas del cierre de caja")


class CashRegisterSummary(BaseModel):
    """Resumen de caja para mostrar en el POS"""
    id: int
    date: date
    status: str
    
    # Inventario
    total_initial_stock: int
    total_current_stock: int
    total_units_sold: int
    total_shrinkage: int
    
    # Ventas
    total_sales_count: int
    total_sales_amount: Decimal
    
    # Por método de pago
    cash_sales: Decimal
    card_sales: Decimal
    transfer_sales: Decimal
    
    # Efectivo
    initial_cash: Decimal
    expected_cash: Decimal
    actual_cash: Optional[Decimal]
    cash_difference: Optional[Decimal]
    
    # Productos
    inventory_details: List[DailyInventoryItem]
    shrinkage_details: List[ShrinkageResponse]


class CashRegisterResponse(BaseModel):
    """Schema completo de respuesta de caja"""
    id: int
    user_id: int
    user_name: Optional[str] = None
    date: date
    status: str
    
    initial_cash: Decimal
    total_sales: Decimal
    total_cash_sales: Decimal
    total_card_sales: Decimal
    total_transfer_sales: Decimal
    
    expected_cash: Decimal
    actual_cash: Optional[Decimal]
    cash_difference: Decimal
    
    closing_notes: Optional[str]
    
    opened_at: datetime
    closed_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


# ========== VENTA CON CAMBIO ==========

class SaleWithChange(BaseModel):
    """
    Schema extendido para venta con cálculo de cambio.
    
    Incluye el dinero recibido y calcula el vuelto automáticamente.
    """
    customer_id: Optional[int] = None
    payment_method: str = Field(..., description="efectivo, tarjeta, transferencia")
    payment_received: Decimal = Field(..., gt=0, description="Dinero recibido del cliente")
    items: List[dict] = Field(..., min_length=1, description="Productos de la venta")
    notes: Optional[str] = None


class ChangeCalculation(BaseModel):
    """Cálculo de vuelto"""
    total: Decimal
    payment_received: Decimal
    change: Decimal
    
    @staticmethod
    def calculate(total: Decimal, payment_received: Decimal):
        """Calcula el vuelto"""
        change = payment_received - total
        return ChangeCalculation(
            total=total,
            payment_received=payment_received,
            change=max(change, Decimal(0))
        )
