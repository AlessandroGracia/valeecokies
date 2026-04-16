"""
Modelos de Venta e Items de Venta.

Sale: Representa una factura/venta completa
SaleItem: Representa cada producto vendido dentro de una factura
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class PaymentMethod(enum.Enum):
    """Métodos de pago disponibles"""
    EFECTIVO = "efectivo"
    TARJETA = "tarjeta"
    TRANSFERENCIA = "transferencia"
    CREDITO = "credito"


class SaleStatus(enum.Enum):
    """Estados de una venta"""
    PENDIENTE = "pendiente"
    COMPLETADA = "completada"
    ANULADA = "anulada"


class Sale(Base):
    """
    Modelo de Venta (Factura).
    
    Representa una transacción de venta completa.
    """
    __tablename__ = "ventas"
    
    # Identificador
    id = Column(Integer, primary_key=True, index=True)
    
    # Número de factura (generado automáticamente)
    invoice_number = Column(String(20), unique=True, index=True, nullable=False)
    
    # Relaciones con otras tablas
    customer_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    # Totales
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax = Column(Numeric(10, 2), default=0)  # IVA u otros impuestos
    discount = Column(Numeric(10, 2), default=0)
    total = Column(Numeric(10, 2), nullable=False)
    
    # Pago
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_received = Column(Numeric(10, 2), nullable=False)
    change_returned = Column(Numeric(10, 2), default=0)
    
    # Estado
    status = Column(Enum(SaleStatus), default=SaleStatus.COMPLETADA)
    
    # Notas
    notes = Column(Text, nullable=True)
    
    # Timestamps
    sale_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones ORM (permite acceder a datos relacionados)
    customer = relationship("Customer", backref="sales")
    user = relationship("User", backref="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Sale {self.invoice_number}: ${self.total}>"


class SaleItem(Base):
    """
    Modelo de Item de Venta.
    
    Representa cada producto individual dentro de una factura.
    """
    __tablename__ = "items_venta"
    
    # Identificador
    id = Column(Integer, primary_key=True, index=True)
    
    # Relaciones
    sale_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    
    # Detalles del item
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)  # Precio al momento de venta
    subtotal = Column(Numeric(10, 2), nullable=False)    # quantity * unit_price
    
    # Descuento individual (opcional)
    discount = Column(Numeric(10, 2), default=0)
    
    # Total del item
    total = Column(Numeric(10, 2), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones ORM
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", backref="sale_items")
    
    def __repr__(self):
        return f"<SaleItem: {self.quantity}x Product#{self.product_id}>"
