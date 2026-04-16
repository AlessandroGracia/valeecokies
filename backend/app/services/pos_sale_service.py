"""
Servicio de Ventas modificado para sistema POS.

Incluye:
- Integración con caja diaria
- Cálculo automático de vuelto
- Descuento de inventario diario
"""

from sqlalchemy.orm import Session
from app.models.sale import Sale, SaleItem, PaymentMethod, SaleStatus
from app.models.product import Product
from app.schemas.sale import SaleCreate
from app.services.cash_register_service import CashRegisterService
from typing import List
from decimal import Decimal
from fastapi import HTTPException, status


class POSSaleService:
    """Servicio de ventas para POS"""
    
    @staticmethod
    def create_sale_with_change(
        db: Session,
        user_id: int,
        customer_id: int,
        items: List[dict],
        payment_method: str,
        payment_received: Decimal,
        notes: str = None
    ) -> dict:
        """
        Crea una venta con cálculo de vuelto.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario vendedor
            customer_id: ID del cliente (opcional)
            items: Lista de items [{"product_id": 1, "quantity": 2}]
            payment_method: Método de pago
            payment_received: Dinero recibido
            notes: Notas adicionales
        
        Returns:
            dict con la venta y el vuelto calculado
        """
        
        # Verificar que hay caja abierta
        if not CashRegisterService.is_cash_register_open(db):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay caja abierta. Abre la caja antes de realizar ventas."
            )
        
        try:
            # Validar productos y calcular totales
            products_data = []
            subtotal = Decimal(0)
            
            for item in items:
                product = db.query(Product).filter(Product.id == item['product_id']).first()
                
                if not product:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Producto con ID {item['product_id']} no encontrado"
                    )
                
                if not product.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"El producto '{product.name}' está inactivo"
                    )
                
                # Verificar stock
                if product.stock_quantity < item['quantity']:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Stock insuficiente para '{product.name}'. Disponible: {product.stock_quantity}"
                    )
                
                # Calcular subtotal del item
                unit_price = product.sale_price
                item_total = unit_price * item['quantity']
                subtotal += item_total
                
                products_data.append({
                    'product': product,
                    'quantity': item['quantity'],
                    'unit_price': unit_price,
                    'total': item_total
                })
            
            # Total de la venta
            total = subtotal
            
            # Validar pago recibido
            if payment_received < total:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Pago insuficiente. Total: ${total}, Recibido: ${payment_received}"
                )
            
            # Calcular vuelto
            change = payment_received - total
            
            # Generar número de factura
            invoice_number = POSSaleService._generate_invoice_number(db)
            
            # Crear venta
            new_sale = Sale(
                invoice_number=invoice_number,
                customer_id=customer_id,
                user_id=user_id,
                subtotal=subtotal,
                tax=Decimal(0),
                discount=Decimal(0),
                total=total,
                payment_method=PaymentMethod(payment_method),
                payment_received=payment_received,
                change_returned=change,
                status=SaleStatus.COMPLETADA,
                notes=notes
            )
            
            db.add(new_sale)
            db.flush()
            
            # Crear items de venta
            sale_items_created = []
            for data in products_data:
                sale_item = SaleItem(
                    sale_id=new_sale.id,
                    product_id=data['product'].id,
                    quantity=data['quantity'],
                    unit_price=data['unit_price'],
                    subtotal=data['total'],
                    discount=Decimal(0),
                    total=data['total']
                )
                db.add(sale_item)
                sale_items_created.append(sale_item)
                
                # Descontar del stock general
                data['product'].stock_quantity -= data['quantity']
            
            # Actualizar inventario diario
            CashRegisterService.update_inventory_on_sale(db, sale_items_created)
            
            db.commit()
            db.refresh(new_sale)
            
            return {
                "sale": new_sale,
                "change": float(change),
                "items": sale_items_created
            }
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear venta: {str(e)}"
            )
    
    
    @staticmethod
    def _generate_invoice_number(db: Session) -> str:
        """Genera número de factura único"""
        from datetime import datetime
        today = datetime.now()
        prefix = f"FAC-{today.strftime('%Y%m%d')}"
        
        last_sale = db.query(Sale).filter(
            Sale.invoice_number.like(f"{prefix}%")
        ).order_by(Sale.invoice_number.desc()).first()
        
        if last_sale:
            last_number = int(last_sale.invoice_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:04d}"
    
    
    @staticmethod
    def calculate_change(total: Decimal, payment_received: Decimal) -> dict:
        """
        Calcula el vuelto antes de confirmar la venta.
        
        Útil para mostrar en la UI antes de procesar.
        """
        if payment_received < total:
            return {
                "valid": False,
                "message": "Pago insuficiente",
                "total": float(total),
                "payment_received": float(payment_received),
                "change": 0
            }
        
        change = payment_received - total
        
        return {
            "valid": True,
            "message": "OK",
            "total": float(total),
            "payment_received": float(payment_received),
            "change": float(change)
        }
