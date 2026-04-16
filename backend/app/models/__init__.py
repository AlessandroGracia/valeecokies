"""
Inicialización del paquete de modelos.

Este archivo permite importar todos los modelos desde un solo lugar.
"""

from app.models.user import User, UserRole
from app.models.product import Product
from app.models.customer import Customer
from app.models.sale import Sale, SaleItem, PaymentMethod, SaleStatus
from app.models.cash_register import (
    DailyCashRegister,
    DailyInventory,
    Shrinkage,
    CashRegisterStatus
)

# Exportar todos los modelos
__all__ = [
    "User",
    "UserRole",
    "Product",
    "Customer",
    "Sale",
    "SaleItem",
    "PaymentMethod",
    "SaleStatus",
    "DailyCashRegister",
    "DailyInventory",
    "Shrinkage",
    "CashRegisterStatus",
]
