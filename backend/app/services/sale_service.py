"""
Servicio de Ventas - Unificado.

Contiene toda la lógica de negocio para gestionar ventas.
Maneja transacciones complejas con productos, inventario y cálculos.

Este servicio unifica la lógica de SaleService y POSSaleService
para evitar duplicación y garantizar consistencia.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, text
from app.models.sale import Sale, SaleItem, PaymentMethod, SaleStatus
from app.models.product import Product
from app.models.customer import Customer
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleUpdate
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal
from fastapi import HTTPException, status


class SaleService:
    """Servicio unificado para gestión de ventas"""
    
    @staticmethod
    def _generate_invoice_number(db: Session) -> str:
        """
        Genera un número de factura único usando bloqueo a nivel de consulta
        para prevenir duplicados en concurrencia.
        
        Formato: FAC-YYYYMMDD-XXXX
        Ejemplo: FAC-20260213-0001
        """
        today = datetime.now()
        prefix = f"FAC-{today.strftime('%Y%m%d')}"
        
        # Usar FOR UPDATE para bloquear la fila y prevenir race conditions
        # Si la DB no soporta FOR UPDATE en esta query, usamos un approach seguro
        last_sale = db.query(Sale).filter(
            Sale.invoice_number.like(f"{prefix}%")
        ).order_by(Sale.invoice_number.desc()).with_for_update().first()
        
        if last_sale:
            # Extraer el número y sumar 1
            last_number = int(last_sale.invoice_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        # Formatear con ceros a la izquierda (4 dígitos)
        return f"{prefix}-{new_number:04d}"
    
    
    @staticmethod
    def _validate_and_prepare_items(
        db: Session, 
        items: list, 
        is_dict: bool = False
    ) -> tuple:
        """
        Valida productos, stock y prepara los datos de items.
        
        Args:
            db: Sesión de base de datos
            items: Lista de items (SaleItemCreate objects o dicts)
            is_dict: Si True, items son dicts (POS); si False, son SaleItemCreate
        
        Returns:
            Tuple de (products_data, subtotal, items_list)
        """
        products_data = []
        subtotal = Decimal(0)
        items_list = []
        
        for item in items:
            product_id = item['product_id'] if is_dict else item.product_id
            quantity = item['quantity'] if is_dict else item.quantity
            item_discount = Decimal(str(item.get('discount', 0))) if is_dict else getattr(item, 'discount', Decimal(0))
            
            # Obtener producto con bloqueo para prevenir race condition en stock
            product = db.query(Product).filter(
                Product.id == product_id
            ).with_for_update().first()
            
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Producto con ID {product_id} no encontrado"
                )
            
            if not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El producto '{product.name}' está inactivo"
                )
            
            if product.stock_quantity < quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stock insuficiente para '{product.name}'. Disponible: {product.stock_quantity}, Solicitado: {quantity}"
                )
            
            # Cálculos del item
            unit_price = product.sale_price
            item_subtotal = unit_price * quantity
            item_total = item_subtotal - item_discount
            
            subtotal += item_total
            
            items_list.append({
                'product_id': product.id,
                'quantity': quantity,
                'unit_price': unit_price,
                'subtotal': item_subtotal,
                'discount': item_discount,
                'total': item_total
            })
            
            products_data.append({
                'product': product,
                'quantity': quantity
            })
        
        return products_data, subtotal, items_list
    
    
    @staticmethod
    def create_sale(
        db: Session, 
        sale_data: SaleCreate, 
        user_id: int,
        update_daily_inventory: bool = False
    ) -> Sale:
        """
        Crea una nueva venta con todos sus items.
        
        Este método maneja transacciones complejas:
        1. Valida stock de productos
        2. Calcula totales
        3. Crea la venta y sus items
        4. Descuenta del inventario
        5. Opcionalmente actualiza inventario diario
        6. Si algo falla, revierte TODO
        
        Args:
            db: Sesión de base de datos
            sale_data: Datos de la venta
            user_id: ID del usuario que hace la venta
            update_daily_inventory: Si True, también actualiza inventario diario
        
        Returns:
            Venta creada
        
        Raises:
            HTTPException: Si hay errores de validación o stock
        """
        
        try:
            # Validar que el usuario existe
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Usuario con ID {user_id} no encontrado"
                )
            
            # Validar cliente si se proporciona
            if sale_data.customer_id:
                customer = db.query(Customer).filter(Customer.id == sale_data.customer_id).first()
                if not customer:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Cliente con ID {sale_data.customer_id} no encontrado"
                    )
            
            # Validar productos y stock
            products_data, subtotal, items_list = SaleService._validate_and_prepare_items(
                db, sale_data.items, is_dict=False
            )
            
            # Calcular total general
            total = subtotal + sale_data.tax - sale_data.discount
            
            # Validar pago recibido
            if sale_data.payment_received < total:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Pago insuficiente. Total: ${total}, Recibido: ${sale_data.payment_received}"
                )
            
            # Calcular cambio
            change = sale_data.payment_received - total
            
            # Generar número de factura
            invoice_number = SaleService._generate_invoice_number(db)
            
            # Crear la venta (cabecera)
            new_sale = Sale(
                invoice_number=invoice_number,
                customer_id=sale_data.customer_id,
                user_id=user_id,
                subtotal=subtotal,
                tax=sale_data.tax,
                discount=sale_data.discount,
                total=total,
                payment_method=PaymentMethod(sale_data.payment_method),
                payment_received=sale_data.payment_received,
                change_returned=change,
                status=SaleStatus.completada,
                notes=sale_data.notes,
                sale_date=datetime.now()
            )
            
            db.add(new_sale)
            db.flush()  # Obtener el ID sin hacer commit
            
            # Crear los items y descontar del inventario
            sale_items_created = []
            for i, item_data in enumerate(items_list):
                sale_item = SaleItem(
                    sale_id=new_sale.id,
                    **item_data
                )
                db.add(sale_item)
                sale_items_created.append(sale_item)
                
                # Descontar del inventario general
                products_data[i]['product'].stock_quantity -= item_data['quantity']
            
            # Actualizar inventario diario si se solicita
            if update_daily_inventory:
                SaleService._update_daily_inventory(db, sale_items_created)
            
            # Commit de toda la transacción
            db.commit()
            db.refresh(new_sale)
            
            return new_sale
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear la venta: {str(e)}"
            )
    
    
    @staticmethod
    def create_pos_sale(
        db: Session,
        user_id: int,
        items: List[dict],
        payment_method: str,
        payment_received: Decimal,
        customer_id: int = None,
        notes: str = None
    ) -> dict:
        """
        Crea una venta desde el POS con cálculo de vuelto.
        Siempre actualiza el inventario diario.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario vendedor
            items: Lista de items [{"product_id": 1, "quantity": 2}]
            payment_method: Método de pago
            payment_received: Dinero recibido
            customer_id: ID del cliente (opcional)
            notes: Notas adicionales
        
        Returns:
            dict con la venta y el vuelto calculado
        """
        
        # Verificar que hay caja abierta
        from app.services.cash_register_service import CashRegisterService
        if not CashRegisterService.is_cash_register_open(db):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay caja abierta. Abre la caja antes de realizar ventas."
            )
        
        try:
            # Validar productos y stock
            products_data, subtotal, items_list = SaleService._validate_and_prepare_items(
                db, items, is_dict=True
            )
            
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
            invoice_number = SaleService._generate_invoice_number(db)
            
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
                status=SaleStatus.completada,
                notes=notes,
                sale_date=datetime.now()
            )
            
            db.add(new_sale)
            db.flush()
            
            # Crear items de venta y descontar stock
            sale_items_created = []
            for i, item_data in enumerate(items_list):
                sale_item = SaleItem(
                    sale_id=new_sale.id,
                    **item_data
                )
                db.add(sale_item)
                sale_items_created.append(sale_item)
                
                # Descontar del stock general
                products_data[i]['product'].stock_quantity -= item_data['quantity']
            
            # Siempre actualizar inventario diario en POS
            SaleService._update_daily_inventory(db, sale_items_created)
            
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
    def _update_daily_inventory(db: Session, sale_items: list):
        """
        Actualiza el inventario diario cuando se hace una venta.
        Si no hay caja abierta, no hace nada.
        """
        from app.services.cash_register_service import CashRegisterService
        CashRegisterService.update_inventory_on_sale(db, sale_items)
    
    
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
    
    
    @staticmethod
    def get_all_sales(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[Sale]:
        """Obtiene todas las ventas con filtros"""
        query = db.query(Sale)
        
        # Filtrar por estado
        if status_filter:
            query = query.filter(Sale.status == SaleStatus(status_filter.lower()))
        
        # Filtrar por rango de fechas
        if date_from:
            query = query.filter(func.date(Sale.sale_date) >= date_from)
        if date_to:
            query = query.filter(func.date(Sale.sale_date) <= date_to)
        
        sales = query.order_by(Sale.sale_date.desc()).offset(skip).limit(limit).all()
        return sales
    
    
    @staticmethod
    def get_sale_by_id(db: Session, sale_id: int) -> Sale:
        """Obtiene una venta por ID"""
        sale = db.query(Sale).filter(Sale.id == sale_id).first()
        
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Venta con ID {sale_id} no encontrada"
            )
        
        return sale
    
    
    @staticmethod
    def cancel_sale(db: Session, sale_id: int) -> Sale:
        """
        Anula una venta y devuelve el stock.
        
        Args:
            db: Sesión de base de datos
            sale_id: ID de la venta a anular
        
        Returns:
            Venta anulada
        """
        sale = SaleService.get_sale_by_id(db, sale_id)
        
        if sale.status == SaleStatus.anulada:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La venta ya está anulada"
            )
        
        try:
            # Devolver productos al inventario
            for item in sale.items:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    product.stock_quantity += item.quantity
            
            # Marcar como anulada
            sale.status = SaleStatus.anulada
            
            db.commit()
            db.refresh(sale)
            
            return sale
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al anular la venta: {str(e)}"
            )
    
    
    @staticmethod
    def get_sales_stats(db: Session, date_from: Optional[date] = None, date_to: Optional[date] = None) -> dict:
        """Obtiene estadísticas de ventas"""
        query = db.query(Sale)
        
        if date_from:
            query = query.filter(func.date(Sale.sale_date) >= date_from)
        if date_to:
            query = query.filter(func.date(Sale.sale_date) <= date_to)
        
        total_sales = query.count()
        completed = query.filter(Sale.status == SaleStatus.completada).count()
        pending = query.filter(Sale.status == SaleStatus.pendiente).count()
        cancelled = query.filter(Sale.status == SaleStatus.anulada).count()
        
        # Total vendido (solo completadas)
        total_amount = db.query(func.sum(Sale.total)).filter(
            Sale.status == SaleStatus.completada
        ).scalar() or Decimal(0)
        
        # Promedio por venta
        average = total_amount / completed if completed > 0 else Decimal(0)
        
        return {
            "total_sales": total_sales,
            "total_amount": float(total_amount),
            "pending_sales": pending,
            "completed_sales": completed,
            "cancelled_sales": cancelled,
            "average_sale": float(average)
        }
    
    
    @staticmethod
    def get_daily_sales(db: Session, target_date: date) -> dict:
        """Obtiene ventas de un día específico"""
        sales = db.query(Sale).filter(
            func.date(Sale.sale_date) == target_date,
            Sale.status == SaleStatus.completada
        ).all()
        
        total_amount = sum(sale.total for sale in sales)
        cash = sum(sale.total for sale in sales if sale.payment_method == PaymentMethod.efectivo)
        card = sum(sale.total for sale in sales if sale.payment_method == PaymentMethod.tarjeta)
        transfer = sum(sale.total for sale in sales if sale.payment_method == PaymentMethod.transferencia)
        
        return {
            "date": target_date.isoformat(),
            "total_sales": len(sales),
            "total_amount": float(total_amount),
            "cash_sales": float(cash),
            "card_sales": float(card),
            "transfer_sales": float(transfer)
        }