"""
Servicio de Productos.

Contiene toda la lógica de negocio para gestionar productos.
Separamos la lógica de negocio de los endpoints (buena práctica).
"""

from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from typing import List, Optional
from fastapi import HTTPException, status


class ProductService:
    """
    Servicio para gestión de productos.
    
    Cada método representa una operación de negocio.
    """
    
    @staticmethod
    def get_all_products(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[Product]:
        """
        Obtiene todos los productos con paginación.
        
        Args:
            db: Sesión de base de datos
            skip: Número de registros a saltar (para paginación)
            limit: Máximo de registros a retornar
            is_active: Filtrar por estado activo/inactivo (opcional)
        
        Returns:
            Lista de productos
        """
        query = db.query(Product)
        
        # Filtrar por estado si se especifica
        if is_active is not None:
            query = query.filter(Product.is_active == is_active)
        
        # Ordenar por nombre y aplicar paginación
        products = query.order_by(Product.name).offset(skip).limit(limit).all()
        return products
    
    
    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Product:
        """
        Obtiene un producto por su ID.
        
        Args:
            db: Sesión de base de datos
            product_id: ID del producto
        
        Returns:
            Producto encontrado
        
        Raises:
            HTTPException: Si el producto no existe
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {product_id} no encontrado"
            )
        
        return product
    
    
    @staticmethod
    def get_product_by_code(db: Session, code: str) -> Optional[Product]:
        """
        Obtiene un producto por su código.
        
        Args:
            db: Sesión de base de datos
            code: Código del producto
        
        Returns:
            Producto encontrado o None
        """
        return db.query(Product).filter(Product.code == code).first()
    
    
    @staticmethod
    def create_product(db: Session, product_data: ProductCreate) -> Product:
        """
        Crea un nuevo producto.
        
        Args:
            db: Sesión de base de datos
            product_data: Datos del producto a crear
        
        Returns:
            Producto creado
        
        Raises:
            HTTPException: Si el código ya existe
        """
        # Verificar que el código no exista
        existing = ProductService.get_product_by_code(db, product_data.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un producto con el código '{product_data.code}'"
            )
        
        # Crear el producto
        new_product = Product(**product_data.model_dump())
        
        db.add(new_product)
        db.commit()
        db.refresh(new_product)  # Obtener datos actualizados (timestamps, etc.)
        
        return new_product
    
    
    @staticmethod
    def update_product(
        db: Session, 
        product_id: int, 
        product_data: ProductUpdate
    ) -> Product:
        """
        Actualiza un producto existente.
        
        Args:
            db: Sesión de base de datos
            product_id: ID del producto a actualizar
            product_data: Nuevos datos del producto
        
        Returns:
            Producto actualizado
        
        Raises:
            HTTPException: Si el producto no existe o el código está duplicado
        """
        # Verificar que el producto existe
        product = ProductService.get_product_by_id(db, product_id)
        
        # Si se está actualizando el código, verificar que no exista
        if product_data.code and product_data.code != product.code:
            existing = ProductService.get_product_by_code(db, product_data.code)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un producto con el código '{product_data.code}'"
                )
        
        # Actualizar solo los campos enviados
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        db.commit()
        db.refresh(product)
        
        return product
    
    
    @staticmethod
    def delete_product(db: Session, product_id: int) -> dict:
        """
        Elimina un producto (borrado suave - marca como inactivo).
        
        Args:
            db: Sesión de base de datos
            product_id: ID del producto a eliminar
        
        Returns:
            Mensaje de confirmación
        
        Raises:
            HTTPException: Si el producto no existe
        """
        product = ProductService.get_product_by_id(db, product_id)
        
        # Borrado suave: marcar como inactivo
        product.is_active = False
        
        db.commit()
        
        return {
            "message": f"Producto '{product.name}' eliminado correctamente",
            "product_id": product_id
        }
    
    
    @staticmethod
    def get_low_stock_products(db: Session) -> List[Product]:
        """
        Obtiene productos con stock bajo (menor o igual al mínimo).
        
        Args:
            db: Sesión de base de datos
        
        Returns:
            Lista de productos con stock bajo
        """
        products = db.query(Product).filter(
            Product.stock_quantity <= Product.min_stock,
            Product.is_active == True
        ).order_by(Product.stock_quantity).all()
        
        return products
    
    
    @staticmethod
    def adjust_stock(
        db: Session, 
        product_id: int, 
        quantity_change: int
    ) -> Product:
        """
        Ajusta el stock de un producto.
        
        Args:
            db: Sesión de base de datos
            product_id: ID del producto
            quantity_change: Cantidad a sumar (+) o restar (-)
        
        Returns:
            Producto actualizado
        
        Raises:
            HTTPException: Si el stock resultante es negativo
        """
        product = ProductService.get_product_by_id(db, product_id)
        
        new_stock = product.stock_quantity + quantity_change
        
        if new_stock < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente. Stock actual: {product.stock_quantity}"
            )
        
        product.stock_quantity = new_stock
        
        db.commit()
        db.refresh(product)
        
        return product