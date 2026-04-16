"""
Router de Productos.

Define todos los endpoints HTTP para gestionar productos.
Cada función es un endpoint de la API.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.product import (
    ProductCreate, 
    ProductUpdate, 
    ProductResponse,
    StockAdjustment
)
from app.services.product_service import ProductService
from app.api.deps import get_current_active_user


# Crear el router
# prefix="/api/products" significa que todas las rutas empiezan con /api/products
router = APIRouter(
    prefix="/api/products",
    tags=["Productos"],  # Organiza la documentación en Swagger
    dependencies=[Depends(get_current_active_user)]
)


@router.get("/", response_model=List[ProductResponse])
def get_all_products(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los productos con paginación.
    
    - **skip**: Número de registros a saltar (default: 0)
    - **limit**: Máximo de registros a retornar (default: 100)
    - **is_active**: Filtrar por estado activo/inactivo (opcional)
    
    Ejemplo: GET /api/products?skip=0&limit=10&is_active=true
    """
    products = ProductService.get_all_products(db, skip, limit, is_active)
    return products


@router.get("/low-stock", response_model=List[ProductResponse])
def get_low_stock_products(db: Session = Depends(get_db)):
    """
    Obtiene productos con stock bajo (menor o igual al mínimo).
    
    Útil para generar alertas de reabastecimiento.
    
    Ejemplo: GET /api/products/low-stock
    """
    products = ProductService.get_low_stock_products(db)
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un producto específico por su ID.
    
    - **product_id**: ID del producto
    
    Ejemplo: GET /api/products/1
    """
    product = ProductService.get_product_by_id(db, product_id)
    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo producto.
    
    Requiere enviar en el body:
    ```json
    {
      "code": "GAL001",
      "name": "Galletas de Chocolate",
      "description": "Deliciosas galletas",
      "cost_price": 2.50,
      "sale_price": 4.00,
      "stock_quantity": 100,
      "min_stock": 20,
      "unit": "paquete"
    }
    ```
    
    Validaciones automáticas:
    - El código debe ser único
    - Precio de venta > Precio de costo
    - Cantidades no negativas
    """
    product = ProductService.create_product(db, product_data)
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza un producto existente.
    
    Solo se actualizan los campos enviados (actualización parcial).
    
    - **product_id**: ID del producto a actualizar
    
    Ejemplo body (solo actualizar precio):
    ```json
    {
      "sale_price": 4.50
    }
    ```
    """
    product = ProductService.update_product(db, product_id, product_data)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina un producto (borrado suave).
    
    El producto se marca como inactivo en lugar de eliminarse físicamente.
    Esto preserva el historial de ventas.
    
    - **product_id**: ID del producto a eliminar
    
    Ejemplo: DELETE /api/products/1
    """
    result = ProductService.delete_product(db, product_id)
    return result


@router.patch("/{product_id}/stock", response_model=ProductResponse)
def adjust_stock(
    product_id: int,
    adjustment: StockAdjustment,
    db: Session = Depends(get_db)
):
    """
    Ajusta el stock de un producto.
    
    Útil para ingresos/egresos de inventario manual.
    
    - **product_id**: ID del producto
    
    Ejemplo body (aumentar 50 unidades):
    ```json
    {
      "quantity_change": 50,
      "reason": "Compra de inventario"
    }
    ```
    
    Ejemplo body (disminuir 10 unidades):
    ```json
    {
      "quantity_change": -10,
      "reason": "Producto dañado"
    }
    ```
    """
    product = ProductService.adjust_stock(db, product_id, adjustment.quantity_change)
    return product