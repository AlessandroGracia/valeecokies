"""
Modelo de Caja Diaria.

Controla el flujo diario de inventario, ventas y cuadre de caja.
"""

from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Date, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class CashRegisterStatus(enum.Enum):
    """Estados de la caja"""
    ABIERTA = "abierta"
    CERRADA = "cerrada"


class DailyCashRegister(Base):
    """
    Modelo de Caja Diaria.
    
    Registra la apertura y cierre de caja cada día.
    """
    __tablename__ = "cajas_diarias"
    
    # Identificador
    id = Column(Integer, primary_key=True, index=True)
    
    # Usuario que abre/cierra
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    # Fecha de la caja
    date = Column(Date, nullable=False, index=True)
    
    # Estado
    status = Column(
        SAEnum(CashRegisterStatus),
        default=CashRegisterStatus.ABIERTA,
        nullable=False
    )
    
    # Monto inicial (efectivo al abrir)
    initial_cash = Column(Numeric(10, 2), default=0)
    
    # Totales calculados al cerrar
    total_sales = Column(Numeric(10, 2), default=0)
    total_cash_sales = Column(Numeric(10, 2), default=0)
    total_card_sales = Column(Numeric(10, 2), default=0)
    total_transfer_sales = Column(Numeric(10, 2), default=0)
    
    # Efectivo que debería haber
    expected_cash = Column(Numeric(10, 2), default=0)
    
    # Efectivo real contado
    actual_cash = Column(Numeric(10, 2), nullable=True)
    
    # Diferencia (sobrante o faltante)
    cash_difference = Column(Numeric(10, 2), default=0)
    
    # Notas del cierre
    closing_notes = Column(Text, nullable=True)
    
    # Timestamps
    opened_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    user = relationship("User", backref="cash_registers")
    inventory_items = relationship("DailyInventory", back_populates="cash_register", cascade="all, delete-orphan")
    shrinkage_items = relationship("Shrinkage", back_populates="cash_register", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DailyCashRegister {self.date} - {self.status.value}>"


class DailyInventory(Base):
    """
    Inventario diario por producto.
    
    Registra el stock inicial de cada producto al abrir caja.
    """
    __tablename__ = "inventario_diario"
    
    # Identificador
    id = Column(Integer, primary_key=True, index=True)
    
    # Relaciones
    cash_register_id = Column(Integer, ForeignKey("cajas_diarias.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    
    # Stock inicial declarado
    initial_stock = Column(Integer, nullable=False)
    
    # Stock actual (se actualiza con cada venta)
    current_stock = Column(Integer, nullable=False)
    
    # Unidades vendidas (calculado: initial_stock - current_stock - shrinkage)
    units_sold = Column(Integer, default=0)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    cash_register = relationship("DailyCashRegister", back_populates="inventory_items")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<DailyInventory Product#{self.product_id}: {self.current_stock}/{self.initial_stock}>"


class Shrinkage(Base):
    """
    Mermas del día.
    
    Registra productos dañados, vencidos o extraviados.
    """
    __tablename__ = "mermas"
    
    # Identificador
    id = Column(Integer, primary_key=True, index=True)
    
    # Relaciones
    cash_register_id = Column(Integer, ForeignKey("cajas_diarias.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    
    # Cantidad de merma
    quantity = Column(Integer, nullable=False)
    
    # Razón de la merma
    reason = Column(String(200), nullable=False)
    
    # Notas adicionales
    notes = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    cash_register = relationship("DailyCashRegister", back_populates="shrinkage_items")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<Shrinkage Product#{self.product_id}: {self.quantity} - {self.reason}>"
