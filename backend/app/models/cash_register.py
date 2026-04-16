"""
Modelo de Caja Diaria.
"""

from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Date, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class CashRegisterStatus(enum.Enum):
    """Nombres en minúsculas para match con DB"""
    abierta = "abierta"
    cerrada = "cerrada"


class DailyCashRegister(Base):
    """
    Modelo de Caja Diaria.
    """
    __tablename__ = "cajas_diarias"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    
    status = Column(
        Enum(CashRegisterStatus),
        default=CashRegisterStatus.abierta,
        nullable=False
    )
    
    initial_cash = Column(Numeric(10, 2), default=0)
    total_sales = Column(Numeric(10, 2), default=0)
    total_cash_sales = Column(Numeric(10, 2), default=0)
    total_card_sales = Column(Numeric(10, 2), default=0)
    total_transfer_sales = Column(Numeric(10, 2), default=0)
    expected_cash = Column(Numeric(10, 2), default=0)
    actual_cash = Column(Numeric(10, 2), nullable=True)
    cash_difference = Column(Numeric(10, 2), default=0)
    closing_notes = Column(Text, nullable=True)
    opened_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User", backref="cash_registers")
    inventory_items = relationship("DailyInventory", back_populates="cash_register", cascade="all, delete-orphan")
    shrinkage_items = relationship("Shrinkage", back_populates="cash_register", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DailyCashRegister {self.date} - {self.status.value}>"


class DailyInventory(Base):
    __tablename__ = "inventario_diario"
    id = Column(Integer, primary_key=True, index=True)
    cash_register_id = Column(Integer, ForeignKey("cajas_diarias.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    initial_stock = Column(Integer, nullable=False)
    current_stock = Column(Integer, nullable=False)
    units_sold = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    cash_register = relationship("DailyCashRegister", back_populates="inventory_items")
    product = relationship("Product")


class Shrinkage(Base):
    __tablename__ = "mermas"
    id = Column(Integer, primary_key=True, index=True)
    cash_register_id = Column(Integer, ForeignKey("cajas_diarias.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    reason = Column(String(200), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    cash_register = relationship("DailyCashRegister", back_populates="shrinkage_items")
    product = relationship("Product")
