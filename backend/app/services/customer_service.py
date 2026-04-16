"""
Servicio de Clientes.

Contiene toda la lógica de negocio para gestionar clientes.
"""

from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from typing import List, Optional
from fastapi import HTTPException, status


class CustomerService:
    """
    Servicio para gestión de clientes.
    """
    
    @staticmethod
    def get_all_customers(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[Customer]:
        """
        Obtiene todos los clientes con paginación y búsqueda.
        
        Args:
            db: Sesión de base de datos
            skip: Número de registros a saltar
            limit: Máximo de registros a retornar
            is_active: Filtrar por estado activo/inactivo
            search: Buscar por nombre, email o teléfono
        
        Returns:
            Lista de clientes
        """
        query = db.query(Customer)
        
        # Filtrar por estado si se especifica
        if is_active is not None:
            query = query.filter(Customer.is_active == is_active)
        
        # Búsqueda por nombre, email o teléfono
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Customer.full_name.ilike(search_filter)) |
                (Customer.email.ilike(search_filter)) |
                (Customer.phone.ilike(search_filter)) |
                (Customer.id_number.ilike(search_filter))
            )
        
        # Ordenar por nombre y aplicar paginación
        customers = query.order_by(Customer.full_name).offset(skip).limit(limit).all()
        return customers
    
    
    @staticmethod
    def get_customer_by_id(db: Session, customer_id: int) -> Customer:
        """
        Obtiene un cliente por su ID.
        
        Args:
            db: Sesión de base de datos
            customer_id: ID del cliente
        
        Returns:
            Cliente encontrado
        
        Raises:
            HTTPException: Si el cliente no existe
        """
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente con ID {customer_id} no encontrado"
            )
        
        return customer
    
    
    @staticmethod
    def get_customer_by_email(db: Session, email: str) -> Optional[Customer]:
        """
        Obtiene un cliente por su email.
        
        Args:
            db: Sesión de base de datos
            email: Email del cliente
        
        Returns:
            Cliente encontrado o None
        """
        return db.query(Customer).filter(Customer.email == email).first()
    
    
    @staticmethod
    def get_customer_by_id_number(db: Session, id_number: str) -> Optional[Customer]:
        """
        Obtiene un cliente por su cédula/RUC.
        
        Args:
            db: Sesión de base de datos
            id_number: Cédula o RUC del cliente
        
        Returns:
            Cliente encontrado o None
        """
        return db.query(Customer).filter(Customer.id_number == id_number).first()
    
    
    @staticmethod
    def create_customer(db: Session, customer_data: CustomerCreate) -> Customer:
        """
        Crea un nuevo cliente.
        
        Args:
            db: Sesión de base de datos
            customer_data: Datos del cliente a crear
        
        Returns:
            Cliente creado
        
        Raises:
            HTTPException: Si el email o cédula ya existen
        """
        # Verificar que el email no exista (si se proporciona)
        if customer_data.email:
            existing = CustomerService.get_customer_by_email(db, customer_data.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un cliente con el email '{customer_data.email}'"
                )
        
        # Verificar que la cédula no exista (si se proporciona)
        if customer_data.id_number:
            existing = CustomerService.get_customer_by_id_number(db, customer_data.id_number)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un cliente con la cédula/RUC '{customer_data.id_number}'"
                )
        
        # Crear el cliente
        new_customer = Customer(**customer_data.model_dump())
        
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)
        
        return new_customer
    
    
    @staticmethod
    def update_customer(
        db: Session,
        customer_id: int,
        customer_data: CustomerUpdate
    ) -> Customer:
        """
        Actualiza un cliente existente.
        
        Args:
            db: Sesión de base de datos
            customer_id: ID del cliente a actualizar
            customer_data: Nuevos datos del cliente
        
        Returns:
            Cliente actualizado
        
        Raises:
            HTTPException: Si el cliente no existe o hay duplicados
        """
        # Verificar que el cliente existe
        customer = CustomerService.get_customer_by_id(db, customer_id)
        
        # Si se está actualizando el email, verificar que no exista
        if customer_data.email and customer_data.email != customer.email:
            existing = CustomerService.get_customer_by_email(db, customer_data.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un cliente con el email '{customer_data.email}'"
                )
        
        # Si se está actualizando la cédula, verificar que no exista
        if customer_data.id_number and customer_data.id_number != customer.id_number:
            existing = CustomerService.get_customer_by_id_number(db, customer_data.id_number)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un cliente con la cédula/RUC '{customer_data.id_number}'"
                )
        
        # Actualizar solo los campos enviados
        update_data = customer_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)
        
        db.commit()
        db.refresh(customer)
        
        return customer
    
    
    @staticmethod
    def delete_customer(db: Session, customer_id: int) -> dict:
        """
        Elimina un cliente (borrado suave - marca como inactivo).
        
        Args:
            db: Sesión de base de datos
            customer_id: ID del cliente a eliminar
        
        Returns:
            Mensaje de confirmación
        
        Raises:
            HTTPException: Si el cliente no existe
        """
        customer = CustomerService.get_customer_by_id(db, customer_id)
        
        # Borrado suave: marcar como inactivo
        customer.is_active = False
        
        db.commit()
        
        return {
            "message": f"Cliente '{customer.full_name}' eliminado correctamente",
            "customer_id": customer_id
        }
    
    
    @staticmethod
    def get_customer_count(db: Session) -> dict:
        """
        Obtiene estadísticas de clientes.
        
        Args:
            db: Sesión de base de datos
        
        Returns:
            Diccionario con contadores
        """
        total = db.query(Customer).count()
        active = db.query(Customer).filter(Customer.is_active == True).count()
        inactive = total - active
        
        return {
            "total": total,
            "active": active,
            "inactive": inactive
        }