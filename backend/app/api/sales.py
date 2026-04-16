"""
Router de Ventas.

Define todos los endpoints HTTP para gestionar ventas (facturación).
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from app.core.database import get_db
from app.schemas.sale import (
    SaleCreate,
    SaleUpdate,
    SaleResponse,
    SaleSummary,
    SalesStats,
    DailySales
)
from app.services.sale_service import SaleService
from app.api.deps import get_current_active_user


# Crear el router
router = APIRouter(
    prefix="/api/sales",
    tags=["Ventas"]
)


@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Crea una nueva venta (factura).
    
    **Este es el endpoint principal para facturación.**
    
    Requiere enviar en el body:
    ```json
    {
      "customer_id": 1,
      "payment_method": "efectivo",
      "payment_received": 20.00,
      "discount": 0,
      "tax": 0,
      "notes": "Venta al por mayor",
      "items": [
        {
          "product_id": 1,
          "quantity": 5,
          "discount": 0
        },
        {
          "product_id": 2,
          "quantity": 3,
          "discount": 0.50
        }
      ]
    }
    ```
    
    **Proceso automático:**
    1. Valida stock disponible
    2. Calcula totales de cada item
    3. Calcula total general
    4. Genera número de factura único
    5. Descuenta del inventario
    6. Calcula cambio
    
    **Métodos de pago válidos:**
    - efectivo
    - tarjeta
    - transferencia
    - credito
    """
    sale = SaleService.create_sale(db, sale_data, current_user.id)
    
    # Enriquecer respuesta con nombres
    if sale.customer:
        sale.customer_name = sale.customer.full_name
    if sale.user:
        sale.user_name = sale.user.full_name
    
    # Enriquecer items con nombres de productos
    for item in sale.items:
        if item.product:
            item.product_name = item.product.name
    
    return sale


from typing import List, Optional, Union

@router.get("/", response_model=List[Union[SaleResponse, SaleSummary]])
def get_all_sales(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filtrar por estado: completada, pendiente, anulada"),
    date_from: Optional[date] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    detailed: bool = Query(False, description="Incluir productos de cada venta"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Obtiene todas las ventas con filtros opcionales.
    """
    sales = SaleService.get_all_sales(db, skip, limit, status, date_from, date_to)
    
    if detailed:
        for sale in sales:
            if sale.customer:
                sale.customer_name = sale.customer.full_name
            if sale.user:
                sale.user_name = sale.user.full_name
            for item in sale.items:
                if item.product:
                    item.product_name = item.product.name
        return sales
    else:
        result = []
        for sale in sales:
            sale_dict = {
                'id': sale.id,
                'invoice_number': sale.invoice_number,
                'customer_name': sale.customer.full_name if sale.customer else "Cliente General",
                'total': sale.total,
                'payment_method': sale.payment_method.value,
                'status': sale.status.value,
                'sale_date': sale.sale_date
            }
            result.append(SaleSummary(**sale_dict))
        return result


@router.get("/stats", response_model=SalesStats)
def get_sales_stats(
    date_from: Optional[date] = Query(None, description="Estadísticas desde esta fecha"),
    date_to: Optional[date] = Query(None, description="Estadísticas hasta esta fecha"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Obtiene estadísticas de ventas.
    
    Retorna:
    - Total de ventas
    - Monto total vendido
    - Ventas completadas, pendientes y anuladas
    - Promedio por venta
    
    Ejemplo: GET /api/sales/stats?date_from=2026-02-01&date_to=2026-02-28
    """
    stats = SaleService.get_sales_stats(db, date_from, date_to)
    return stats


@router.get("/daily", response_model=DailySales)
def get_daily_sales(
    target_date: date = Query(..., description="Fecha a consultar (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Obtiene las ventas de un día específico con desglose por método de pago.
    
    Útil para cuadre de caja diario.
    
    - **target_date**: Fecha a consultar
    
    Ejemplo: GET /api/sales/daily?target_date=2026-02-13
    """
    daily_sales = SaleService.get_daily_sales(db, target_date)
    return daily_sales


@router.get("/today", response_model=DailySales)
def get_today_sales(db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Obtiene las ventas de HOY con desglose por método de pago.
    
    Atajo para cuadre de caja del día actual.
    
    Ejemplo: GET /api/sales/today
    """
    today = date.today()
    daily_sales = SaleService.get_daily_sales(db, today)
    return daily_sales


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Obtiene una venta específica por su ID con todos los detalles.
    
    Incluye:
    - Información de la venta
    - Cliente
    - Vendedor
    - Todos los items con detalles de productos
    
    Ejemplo: GET /api/sales/1
    """
    sale = SaleService.get_sale_by_id(db, sale_id)
    
    # Enriquecer respuesta
    if sale.customer:
        sale.customer_name = sale.customer.full_name
    if sale.user:
        sale.user_name = sale.user.full_name
    
    for item in sale.items:
        if item.product:
            item.product_name = item.product.name
    
    return sale


@router.post("/{sale_id}/cancel", response_model=SaleResponse)
def cancel_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Anula una venta y devuelve el stock al inventario.
    
    **IMPORTANTE:** Esta acción:
    - Marca la venta como anulada
    - Devuelve todos los productos al inventario
    - NO se puede deshacer
    
    Ejemplo: POST /api/sales/1/cancel
    """
    sale = SaleService.cancel_sale(db, sale_id)
    
    # Enriquecer respuesta
    if sale.customer:
        sale.customer_name = sale.customer.full_name
    if sale.user:
        sale.user_name = sale.user.full_name
    
    for item in sale.items:
        if item.product:
            item.product_name = item.product.name
    
    return sale