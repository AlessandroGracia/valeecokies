"""
Router de Caja Diaria.

Endpoints para abrir, operar y cerrar caja.
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas.cash_register import (
    CashRegisterOpen,
    CashRegisterClose,
    CashRegisterResponse,
    CashRegisterSummary,
    ShrinkageCreate,
    ShrinkageResponse
)
from app.services.cash_register_service import CashRegisterService
from app.api.deps import get_current_active_user


router = APIRouter(
    prefix="/api/cash-register",
    tags=["Caja Diaria"]
)


@router.post("/open", response_model=CashRegisterResponse, status_code=status.HTTP_201_CREATED)
def open_cash_register(
    data: CashRegisterOpen,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Abre la caja del día e inicializa el inventario.
    
    **Proceso:**
    1. Registrar efectivo inicial
    2. Declarar inventario inicial de cada producto
    3. Abrir caja para ventas
    
    **Ejemplo de body:**
    ```json
    {
      "initial_cash": 50.00,
      "inventory_items": [
        {
          "product_id": 1,
          "initial_stock": 50
        },
        {
          "product_id": 2,
          "initial_stock": 30
        }
      ]
    }
    ```
    
    Solo se puede abrir una caja por día.
    """
    cash_register = CashRegisterService.open_cash_register(db, current_user.id, data)
    
    # Enriquecer respuesta
    if cash_register.user:
        cash_register.user_name = cash_register.user.full_name
    
    return cash_register


@router.get("/status")
def get_cash_register_status(db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Verifica si hay caja abierta hoy.
    
    Retorna:
    - is_open: True/False
    - date: Fecha de la caja (si existe)
    """
    is_open = CashRegisterService.is_cash_register_open(db)
    cash_register = CashRegisterService.get_today_cash_register(db)
    
    return {
        "is_open": is_open,
        "date": cash_register.date if cash_register else None,
        "status": cash_register.status.value if cash_register else None
    }


@router.get("/summary", response_model=CashRegisterSummary)
def get_cash_register_summary(db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Obtiene el resumen completo de la caja actual.
    
    **Incluye:**
    - Estado de caja (abierta/cerrada)
    - Inventario inicial y actual
    - Unidades vendidas
    - Mermas registradas
    - Ventas del día
    - Cuadre de efectivo
    
    **Úsalo para:**
    - Mostrar en pantalla durante el día
    - Panel de resumen de caja
    - Verificar stock disponible
    """
    return CashRegisterService.get_cash_register_summary(db)


@router.post("/shrinkage", response_model=ShrinkageResponse, status_code=status.HTTP_201_CREATED)
def register_shrinkage(
    shrinkage_data: ShrinkageCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Registra una merma (producto dañado, vencido o extraviado).
    
    **Ejemplo de body:**
    ```json
    {
      "product_id": 1,
      "quantity": 3,
      "reason": "Producto dañado",
      "notes": "Se cayeron al piso"
    }
    ```
    
    La merma descuenta del inventario diario pero no del stock general.
    """
    shrinkage = CashRegisterService.register_shrinkage(db, shrinkage_data)
    
    # Enriquecer con nombre del producto
    if shrinkage.product:
        shrinkage.product_name = shrinkage.product.name
    
    return shrinkage


@router.post("/close", response_model=CashRegisterResponse)
def close_cash_register(
    data: CashRegisterClose,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Cierra la caja del día y hace el cuadre.
    
    **Proceso:**
    1. Calcula totales de ventas
    2. Calcula efectivo esperado
    3. Compara con efectivo real contado
    4. Genera reporte de diferencia
    5. Cierra caja
    
    **Ejemplo de body:**
    ```json
    {
      "actual_cash": 320.50,
      "closing_notes": "Todo en orden. Pequeño sobrante de $0.50"
    }
    ```
    
    **Retorna:**
    - Resumen completo del día
    - Diferencia de efectivo (sobrante o faltante)
    - Inventario vendido vs inicial
    """
    cash_register = CashRegisterService.close_cash_register(db, data)
    
    # Enriquecer respuesta
    if cash_register.user:
        cash_register.user_name = cash_register.user.full_name
    
    return cash_register


@router.get("/today", response_model=Optional[CashRegisterResponse])
def get_today_cash_register(db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Obtiene la caja del día actual (abierta o cerrada).
    
    Retorna None si no hay caja registrada para hoy.
    """
    cash_register = CashRegisterService.get_today_cash_register(db)
    
    if not cash_register:
        return None
    
    # Enriquecer respuesta
    if cash_register.user:
        cash_register.user_name = cash_register.user.full_name
    
    return cash_register
