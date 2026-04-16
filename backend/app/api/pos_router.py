"""
Router de Punto de Venta (POS).

Endpoints específicos para el sistema POS.
Usa el SaleService unificado para evitar duplicación de lógica.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from app.core.database import get_db
from app.services.sale_service import SaleService
from app.api.deps import get_current_active_user


router = APIRouter(
    prefix="/api/pos",
    tags=["Punto de Venta"]
)


from app.schemas.cash_register import SaleWithChange

@router.post("/sale", status_code=status.HTTP_201_CREATED)
def create_pos_sale(
    sale_data: SaleWithChange,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Crea una venta desde el POS con cálculo automático de vuelto.
    
    **Ejemplo de body:**
    ```json
    {
      "user_id": 1,
      "customer_id": null,
      "items": [
        {
          "product_id": 1,
          "quantity": 2
        },
        {
          "product_id": 3,
          "quantity": 1
        }
      ],
      "payment_method": "efectivo",
      "payment_received": 20.00,
      "notes": "Cliente frecuente"
    }
    ```
    
    **Proceso automático:**
    1. Valida stock disponible
    2. Calcula total
    3. Valida pago recibido
    4. Calcula vuelto
    5. Descuenta de inventario general
    6. Descuenta de inventario diario
    7. Retorna venta y vuelto
    """
    
    result = SaleService.create_pos_sale(
        db=db,
        user_id=current_user.id,
        customer_id=sale_data.customer_id,
        items=sale_data.items,
        payment_method=sale_data.payment_method,
        payment_received=sale_data.payment_received,
        notes=sale_data.notes
    )
    
    # Formatear respuesta
    sale = result['sale']
    
    return {
        "invoice_number": sale.invoice_number,
        "total": float(sale.total),
        "payment_received": float(sale.payment_received),
        "change": result['change'],
        "items_count": len(result['items']),
        "sale_id": sale.id,
        "message": f"Venta exitosa. Vuelto: ${result['change']:.2f}"
    }


@router.post("/calculate-change")
def calculate_change(
    total: float,
    payment_received: float,
    db: Session = Depends(get_db)
):
    """
    Calcula el vuelto antes de procesar la venta.
    
    **Útil para:**
    - Mostrar vuelto en tiempo real mientras el usuario ingresa el monto
    - Validar que el pago es suficiente
    """
    
    return SaleService.calculate_change(
        Decimal(str(total)),
        Decimal(str(payment_received))
    )
