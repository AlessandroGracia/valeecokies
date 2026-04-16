"""
Servicio de Caja Diaria.

Maneja todo el flujo de apertura, operación y cierre de caja.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.cash_register import DailyCashRegister, DailyInventory, Shrinkage, CashRegisterStatus
from app.models.sale import Sale, SaleItem, PaymentMethod, SaleStatus
from app.models.product import Product
from app.schemas.cash_register import (
    CashRegisterOpen, 
    CashRegisterClose,
    ShrinkageCreate,
    CashRegisterSummary
)
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from fastapi import HTTPException, status


class CashRegisterService:
    """Servicio para gestión de caja diaria"""
    
    @staticmethod
    def get_today_cash_register(db: Session) -> Optional[DailyCashRegister]:
        """Obtiene la caja del día actual (la más reciente)"""
        today = date.today()
        return db.query(DailyCashRegister).filter(
            DailyCashRegister.date == today
        ).order_by(DailyCashRegister.id.desc()).first()
    
    
    @staticmethod
    def is_cash_register_open(db: Session) -> bool:
        """Verifica si hay una caja abierta hoy"""
        cash_register = CashRegisterService.get_today_cash_register(db)
        return cash_register is not None and cash_register.status == CashRegisterStatus.abierta
    
    
    @staticmethod
    def open_cash_register(
        db: Session, 
        user_id: int, 
        data: CashRegisterOpen
    ) -> DailyCashRegister:
        """
        Abre la caja del día e inicializa el inventario.
        
        Proceso:
        1. Verificar que no exista caja abierta
        2. Crear registro de caja
        3. Registrar inventario inicial de cada producto
        """
        
        # Verificar que no haya caja abierta
        if CashRegisterService.is_cash_register_open(db):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una caja abierta para hoy"
            )
        
        try:
            # Crear caja diaria
            cash_register = DailyCashRegister(
                user_id=user_id,
                date=date.today(),
                status=CashRegisterStatus.abierta,
                initial_cash=data.initial_cash,
                opened_at=datetime.now()
            )
            
            db.add(cash_register)
            db.flush()  # Obtener ID
            
            # Registrar inventario inicial de cada producto
            for item in data.inventory_items:
                # Verificar que el producto existe
                product = db.query(Product).filter(Product.id == item.product_id).first()
                if not product:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Producto con ID {item.product_id} no encontrado"
                    )
                
                # Crear registro de inventario diario
                inventory = DailyInventory(
                    cash_register_id=cash_register.id,
                    product_id=item.product_id,
                    initial_stock=item.initial_stock,
                    current_stock=item.initial_stock,  # Al inicio es igual
                    units_sold=0
                )
                db.add(inventory)
            
            db.commit()
            db.refresh(cash_register)
            
            return cash_register
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al abrir caja: {str(e)}"
            )
    
    
    @staticmethod
    def register_shrinkage(
        db: Session,
        shrinkage_data: ShrinkageCreate
    ) -> Shrinkage:
        """
        Registra una merma.
        
        Descuenta del inventario actual pero no cuenta como venta.
        """
        
        # Verificar que hay caja abierta
        cash_register = CashRegisterService.get_today_cash_register(db)
        if not cash_register or cash_register.status != CashRegisterStatus.abierta:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay caja abierta para registrar mermas"
            )
        
        # Obtener inventario del producto
        inventory = db.query(DailyInventory).filter(
            and_(
                DailyInventory.cash_register_id == cash_register.id,
                DailyInventory.product_id == shrinkage_data.product_id
            )
        ).first()
        
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado en el inventario del día"
            )
        
        # Verificar stock suficiente
        if inventory.current_stock < shrinkage_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente. Disponible: {inventory.current_stock}"
            )
        
        try:
            # Registrar merma
            shrinkage = Shrinkage(
                cash_register_id=cash_register.id,
                product_id=shrinkage_data.product_id,
                quantity=shrinkage_data.quantity,
                reason=shrinkage_data.reason,
                notes=shrinkage_data.notes
            )
            db.add(shrinkage)
            
            # Descontar del inventario actual
            inventory.current_stock -= shrinkage_data.quantity
            
            db.commit()
            db.refresh(shrinkage)
            
            return shrinkage
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al registrar merma: {str(e)}"
            )
    
    
    @staticmethod
    def close_cash_register(
        db: Session,
        data: CashRegisterClose
    ) -> DailyCashRegister:
        """
        Cierra la caja del día y hace el cuadre.
        
        Proceso:
        1. Obtener caja abierta
        2. Calcular totales de ventas
        3. Calcular efectivo esperado
        4. Comparar con efectivo real
        5. Cerrar caja
        """
        
        # Obtener caja abierta
        cash_register = CashRegisterService.get_today_cash_register(db)
        if not cash_register or cash_register.status != CashRegisterStatus.abierta:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay caja abierta para cerrar"
            )
        
        try:
            # Obtener ventas ocurridas durante el turno de esta caja
            sales = db.query(Sale).filter(
                and_(
                    Sale.sale_date >= cash_register.opened_at,
                    Sale.status == SaleStatus.completada
                )
            ).all()
            
            # Calcular totales
            total_sales = sum(sale.total for sale in sales)
            cash_sales = sum(
                sale.total for sale in sales 
                if sale.payment_method == PaymentMethod.efectivo
            )
            card_sales = sum(
                sale.total for sale in sales 
                if sale.payment_method == PaymentMethod.tarjeta
            )
            transfer_sales = sum(
                sale.total for sale in sales 
                if sale.payment_method == PaymentMethod.transferencia
            )
            
            # Efectivo esperado = inicial + ventas en efectivo
            expected_cash = cash_register.initial_cash + cash_sales
            
            # Diferencia
            cash_difference = data.actual_cash - expected_cash
            
            # Actualizar unidades vendidas en inventario
            for inventory in cash_register.inventory_items:
                # Unidades vendidas = inicial - actual - mermas
                shrinkage_qty = db.query(func.sum(Shrinkage.quantity)).filter(
                    and_(
                        Shrinkage.cash_register_id == cash_register.id,
                        Shrinkage.product_id == inventory.product_id
                    )
                ).scalar() or 0
                
                inventory.units_sold = inventory.initial_stock - inventory.current_stock - shrinkage_qty
            
            # Actualizar caja
            cash_register.total_sales = total_sales
            cash_register.total_cash_sales = cash_sales
            cash_register.total_card_sales = card_sales
            cash_register.total_transfer_sales = transfer_sales
            cash_register.expected_cash = expected_cash
            cash_register.actual_cash = data.actual_cash
            cash_register.cash_difference = cash_difference
            cash_register.closing_notes = data.closing_notes
            cash_register.status = CashRegisterStatus.cerrada
            cash_register.closed_at = datetime.now()
            
            db.commit()
            db.refresh(cash_register)
            
            return cash_register
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al cerrar caja: {str(e)}"
            )
    
    
    @staticmethod
    def get_cash_register_summary(db: Session) -> CashRegisterSummary:
        """
        Obtiene el resumen de la caja actual.
        
        Incluye:
        - Estado de caja
        - Inventario (inicial, actual, vendido)
        - Ventas del día
        - Mermas
        - Efectivo
        """
        
        cash_register = CashRegisterService.get_today_cash_register(db)
        if not cash_register:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay caja registrada para hoy"
            )
        
        # Obtener inventario con nombres de productos
        inventory_details = []
        total_initial = 0
        total_current = 0
        total_sold = 0
        
        for inv in cash_register.inventory_items:
            product = inv.product
            inventory_details.append({
                'product_id': inv.product_id,
                'product_name': product.name,
                'initial_stock': inv.initial_stock,
                'current_stock': inv.current_stock,
                'units_sold': inv.units_sold
            })
            total_initial += inv.initial_stock
            total_current += inv.current_stock
            total_sold += inv.units_sold
        
        # Obtener mermas
        shrinkage_details = []
        total_shrinkage = 0
        
        for shrink in cash_register.shrinkage_items:
            product = shrink.product
            shrinkage_details.append({
                'id': shrink.id,
                'product_id': shrink.product_id,
                'product_name': product.name,
                'quantity': shrink.quantity,
                'reason': shrink.reason,
                'notes': shrink.notes,
                'created_at': shrink.created_at
            })
            total_shrinkage += shrink.quantity
        
        # Obtener ventas ocurridas durante el turno de esta caja
        query = db.query(Sale).filter(Sale.status == SaleStatus.completada)
        if cash_register.closed_at:
            sales = query.filter(and_(
                Sale.sale_date >= cash_register.opened_at,
                Sale.sale_date <= cash_register.closed_at
            )).all()
        else:
            sales = query.filter(Sale.sale_date >= cash_register.opened_at).all()
        
        sales_count = len(sales)
        live_total_sales = sum(sale.total for sale in sales)
        live_cash_sales = sum(sale.total for sale in sales if sale.payment_method == PaymentMethod.efectivo)
        live_card_sales = sum(sale.total for sale in sales if sale.payment_method == PaymentMethod.tarjeta)
        live_transfer_sales = sum(sale.total for sale in sales if sale.payment_method == PaymentMethod.transferencia)
        
        # Efectivo esperado en tiempo real = base inicial + ventas en efectivo (si está abierta)
        expected_cash_live = cash_register.initial_cash + live_cash_sales if cash_register.status == CashRegisterStatus.abierta else cash_register.expected_cash
        
        return CashRegisterSummary(
            id=cash_register.id,
            date=cash_register.date,
            status=cash_register.status.value,
            total_initial_stock=total_initial,
            total_current_stock=total_current,
            total_units_sold=total_sold,
            total_shrinkage=total_shrinkage,
            total_sales_count=sales_count,
            total_sales_amount=live_total_sales if cash_register.status == CashRegisterStatus.abierta else cash_register.total_sales,
            cash_sales=live_cash_sales if cash_register.status == CashRegisterStatus.abierta else cash_register.total_cash_sales,
            card_sales=live_card_sales if cash_register.status == CashRegisterStatus.abierta else cash_register.total_card_sales,
            transfer_sales=live_transfer_sales if cash_register.status == CashRegisterStatus.abierta else cash_register.total_transfer_sales,
            initial_cash=cash_register.initial_cash,
            expected_cash=expected_cash_live,
            actual_cash=cash_register.actual_cash,
            cash_difference=cash_register.cash_difference,
            inventory_details=inventory_details,
            shrinkage_details=shrinkage_details
        )
    
    
    @staticmethod
    def update_inventory_on_sale(
        db: Session,
        sale_items: list
    ):
        """
        Actualiza el inventario diario cuando se hace una venta.
        
        Llámalo desde el servicio de ventas después de crear la venta.
        """
        
        cash_register = CashRegisterService.get_today_cash_register(db)
        if not cash_register or cash_register.status != CashRegisterStatus.abierta:
            # Si no hay caja abierta, no actualizar inventario diario
            # (el inventario general del producto ya se descuenta en el servicio de ventas)
            return
        
        # Actualizar inventario diario
        for item in sale_items:
            inventory = db.query(DailyInventory).filter(
                and_(
                    DailyInventory.cash_register_id == cash_register.id,
                    DailyInventory.product_id == item.product_id
                )
            ).first()
            
            if inventory:
                inventory.current_stock -= item.quantity
                inventory.units_sold += item.quantity
        
        db.commit()
