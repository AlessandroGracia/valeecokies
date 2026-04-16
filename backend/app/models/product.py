"""
Modelo de Producto (Galletas).

Define la estructura de la tabla 'productos' que almacena
el inventario de galletas.
"""

from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Product(Base):
    """
    Modelo de Producto.
    
    Representa cada tipo de galleta en el inventario.
    """
    __tablename__ = "productos"
    
    # Identificador único
    id = Column(Integer, primary_key=True, index=True)
    
    # Información del producto
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), default="cookies")  # cookies, bebidas, postres
    
    # Precios
    # Numeric es mejor que Float para dinero (evita errores de redondeo)
    cost_price = Column(Numeric(10, 2), nullable=False)  # Precio de costo
    sale_price = Column(Numeric(10, 2), nullable=False)  # Precio de venta
    
    # Inventario
    stock_quantity = Column(Integer, default=0)
    min_stock = Column(Integer, default=10)  # Stock mínimo para alertas
    
    # Unidad de medida
    unit = Column(String(20), default="unidad")  # unidad, caja, kg, etc.
    
    # Estado
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Product {self.code}: {self.name} (Stock: {self.stock_quantity})>"
    
    @property
    def needs_restock(self) -> bool:
        """Verifica si el producto necesita reabastecimiento"""
        return self.stock_quantity <= self.min_stock
    
    @property
    def profit_margin(self) -> float:
        """Calcula el margen de ganancia en porcentaje"""
        if self.cost_price == 0:
            return 0
        return float(((self.sale_price - self.cost_price) / self.cost_price) * 100)
