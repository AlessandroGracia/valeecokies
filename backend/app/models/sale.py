"""
Modelos de Venta e Items de Venta.
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class PaymentMethod(enum.Enum):
    """Métodos de pago en minúsculas para match con DB"""
    efectivo = "efectivo"
    tarjeta = "tarjeta"
    transferencia = "transferencia"
    credito = "credito"


class SaleStatus(enum.Enum):
    """Estados en minúsculas para match con DB"""
    pendiente = "pendiente"
    completada = "completada"
    anulada = "anulada"


class Sale(Base):
    """
    Modelo de Venta (Factura).
    """
    __tablename__ = "ventas"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(20), unique=True, index=True, nullable=False)
    
    customer_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax = Column(Numeric(10, 2), default=0)
    discount = Column(Numeric(10, 2), default=0)
    total = Column(Numeric(10, 2), nullable=False)
    
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_received = Column(Numeric(10, 2), nullable=False)
    change_returned = Column(Numeric(10, 2), default=0)
    
    status = Column(Enum(SaleStatus), default=SaleStatus.completada)
    
    notes = Column(Text, nullable=True)
    sale_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    customer = relationship("Customer", backref="sales")
    user = relationship("User", backref="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Sale {self.invoice_number}: ${self.total}>"


class SaleItem(Base):
    __tablename__ = "items_venta"
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    discount = Column(Numeric(10, 2), default=0)
    total = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", backref="sale_items")
