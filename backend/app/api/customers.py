"""
Router de Clientes.

Define todos los endpoints HTTP para gestionar clientes.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerSummary
)
from app.services.customer_service import CustomerService
from app.api.deps import get_current_active_user


# Crear el router
router = APIRouter(
    prefix="/api/customers",
    tags=["Clientes"],
    dependencies=[Depends(get_current_active_user)]
)


@router.get("/", response_model=List[CustomerResponse])
def get_all_customers(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los clientes con paginación y búsqueda.
    
    - **skip**: Número de registros a saltar (default: 0)
    - **limit**: Máximo de registros a retornar (default: 100)
    - **is_active**: Filtrar por estado activo/inactivo (opcional)
    - **search**: Buscar por nombre, email, teléfono o cédula (opcional)
    
    Ejemplo: GET /api/customers?skip=0&limit=10&search=maria
    """
    customers = CustomerService.get_all_customers(db, skip, limit, is_active, search)
    return customers


@router.get("/summary", response_model=List[CustomerSummary])
def get_customers_summary(
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """
    Obtiene un listado resumido de clientes.
    
    Útil para dropdowns y selección rápida.
    Solo muestra clientes activos por defecto.
    
    Ejemplo: GET /api/customers/summary
    """
    customers = CustomerService.get_all_customers(db, skip=0, limit=1000, is_active=is_active)
    return customers


@router.get("/stats")
def get_customer_stats(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas de clientes.
    
    Retorna total de clientes, activos e inactivos.
    
    Ejemplo: GET /api/customers/stats
    """
    stats = CustomerService.get_customer_count(db)
    return stats


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un cliente específico por su ID.
    
    - **customer_id**: ID del cliente
    
    Ejemplo: GET /api/customers/1
    """
    customer = CustomerService.get_customer_by_id(db, customer_id)
    return customer


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo cliente.
    
    Requiere enviar en el body:
    ```json
    {
      "full_name": "María González",
      "email": "maria@ejemplo.com",
      "phone": "0999999999",
      "id_number": "0123456789",
      "address": "Av. Principal 123",
      "city": "Quito",
      "notes": "Cliente preferencial"
    }
    ```
    
    Solo el nombre es obligatorio, los demás campos son opcionales.
    
    Validaciones automáticas:
    - Email debe ser válido (si se proporciona)
    - Email único (no puede haber duplicados)
    - Cédula/RUC único (si se proporciona)
    """
    customer = CustomerService.create_customer(db, customer_data)
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza un cliente existente.
    
    Solo se actualizan los campos enviados (actualización parcial).
    
    - **customer_id**: ID del cliente a actualizar
    
    Ejemplo body (solo actualizar teléfono):
    ```json
    {
      "phone": "0988888888"
    }
    ```
    """
    customer = CustomerService.update_customer(db, customer_id, customer_data)
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_200_OK)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina un cliente (borrado suave).
    
    El cliente se marca como inactivo en lugar de eliminarse físicamente.
    Esto preserva el historial de ventas.
    
    - **customer_id**: ID del cliente a eliminar
    
    Ejemplo: DELETE /api/customers/1
    """
    result = CustomerService.delete_customer(db, customer_id)
    return result